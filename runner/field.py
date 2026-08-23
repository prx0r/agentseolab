#!/usr/bin/env python3
"""Field trace extractor + ingester (agentseo-field protocol v1).

Deterministic extraction of search/open/citation events from a recorded Hermes
session (profiles/<p>/state.db messages table) into:
  runs/field/<trial_dir>/trace_raw.json   (immutable raw extraction, written first)
  lab.db field_trials + search_queries + observations  (transactional ingest)

No judgments: every event comes from parsing recorded tool calls / outputs.
Unmappable actions become event_type='tool_invocation', payload.mapped=false.

Usage:
  python3 runner/field.py extract --profile scout --session <sid> \
      --intent-id intent_... --intent-hash <hash> --out runs/field/<dir>
  python3 runner/field.py ingest --trace runs/field/<dir>/trace_raw.json \
      --db lab.db
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import uuid

SEARCH_TOOLS = {"web_search", "browser_search", "search"}
NAVIGATE_TOOLS = {"browser_navigate", "open_url", "web_open"}
SEARCH_ENGINE_HOSTS = (
    "google.com", "bing.com", "duckduckgo.com", "search.brave.com",
    "www.google.com", "www.bing.com", "lite.duckduckgo.com", "html.duckduckgo.com",
)
URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)

EVENT_TYPES_SCHEMA = {
    "search_query", "search_results", "result_open", "citation",
    "final_choice", "rationale", "tool_invocation",
}


def now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def host_of(url):
    m = re.match(r"https?://([^/]+)", url or "")
    return (m.group(1).lower() if m else "")


def is_search_engine(url):
    h = host_of(url)
    return any(h == s or h.endswith("." + s) for s in SEARCH_ENGINE_HOSTS)


def canonical_hash(obj):
    """RFC8785-style: recursive key sort then sha256 — mirrors models.rs."""
    def canon(v):
        if isinstance(v, dict):
            return {k: canon(v[k]) for k in sorted(v.keys())}
        if isinstance(v, list):
            return [canon(x) for x in v]
        return v
    return hashlib.sha256(json.dumps(
        canon(obj), sort_keys=False, separators=(",", ":")).encode()).hexdigest()


def load_session_messages(state_db_path, session_id):
    """Messages for a trial session PLUS its direct subagent sessions (one
    level; delegation verified non-nested across S1-S3 on 2026-08-23).

    Delegation is part of the subject's behavior, so subagent tool calls are
    real search/open events of the same trial. Every merged row carries its
    origin session id (`session_id` key) so provenance stays explicit and
    events remain attributable; nothing is silently relabeled.
    """
    con = sqlite3.connect(f"file:{state_db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    children = [r["id"] for r in con.execute(
        "SELECT id FROM sessions WHERE parent_session_id=? AND source='subagent' "
        "ORDER BY id", (session_id,))]
    rows = []
    for sid in [session_id] + children:
        for r in con.execute(
            "SELECT id, role, content, tool_name, tool_calls, timestamp "
            "FROM messages WHERE session_id=? ORDER BY id", (sid,)):
            d = dict(r)
            d["_origin_session"] = sid
            rows.append(d)
    con.close()
    # chronological interleave; ties: main session before its subagents
    rows.sort(key=lambda r: (r["timestamp"] if r["timestamp"] is not None else 0,
                             0 if r["_origin_session"] == session_id else 1,
                             r["id"]))
    out = []
    for r in rows:
        tcs = []
        if r["tool_calls"]:
            raw = r["tool_calls"]
            try:
                tcs = json.loads(raw) if isinstance(raw, str) else raw
            except json.JSONDecodeError:
                tcs = []
        out.append({
            "id": r["id"], "role": r["role"],
            "content": r["content"] or "",
            "tool_name": r["tool_name"],
            "session_id": r["_origin_session"],
            "tool_calls": [
                {
                    "call_id": tc.get("id") or tc.get("call_id"),
                    "name": ((tc.get("function") or {}).get("name")
                             if isinstance(tc.get("function"), dict)
                             else None) or tc.get("name"),
                    "arguments": ((tc.get("function") or {}).get("arguments")
                                  if isinstance(tc.get("function"), dict)
                                  else None) or "{}",
                } if isinstance(tc, dict) else {"call_id": None, "name": None,
                                                "arguments": "{}"}
                for tc in tcs
            ],
            "timestamp": r["timestamp"],
        })
    return out


def parse_args_obj(args_str):
    try:
        v = json.loads(args_str)
        return v if isinstance(v, dict) else {"value": v}
    except json.JSONDecodeError:
        return {"raw": str(args_str)[:500]}


def extract_events(messages):
    """Walk the message list once; emit ordered events. Deterministic."""
    events = []
    call_index = {}       # call_id -> emitted search_query index (for results join)
    seq = 0
    for msg in messages:
        # tolerate raw rows where tool_calls is still a JSON string
        raw_calls = msg.get("tool_calls")
        if isinstance(raw_calls, str):
            try:
                raw_calls = json.loads(raw_calls)
            except json.JSONDecodeError:
                raw_calls = []
        # --- assistant tool calls ---
        for tc in raw_calls or []:
            if isinstance(tc, str):
                try:
                    tc = json.loads(tc)
                except json.JSONDecodeError:
                    continue
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function") if isinstance(tc.get("function"), dict) else {}
            name = (fn.get("name") or tc.get("name") or "")
            args = parse_args_obj(fn.get("arguments")
                                  or tc.get("arguments") or "{}")
            cid = tc.get("id") or tc.get("call_id")
            base = {
                "seq": seq,
                "ts": msg["timestamp"],
                "source_message_id": msg["id"],
                "origin_session": msg.get("session_id"),
                "call_id": cid,
            }
            seq += 1
            if name in SEARCH_TOOLS:
                q = args.get("query") or args.get("q") or args.get("search")
                ev = {**base, "event_type": "search_query",
                      "payload": {"query": q if isinstance(q, str) else json.dumps(args)[:300],
                                  "tool": name}}
                call_index[cid] = len(events)
                events.append(ev)
            elif name in NAVIGATE_TOOLS:
                url = args.get("url") or args.get("u") or ""
                if isinstance(url, str) and url.startswith("http"):
                    if is_search_engine(url):
                        ev = {**base, "event_type": "search_results",
                              "payload": {"url": url, "note":
                                          "navigation-to-search-engine (result parse deferred to tool output)",
                                          "tool": name}}
                    else:
                        ev = {**base, "event_type": "result_open",
                              "payload": {"url": url, "tool": name}}
                    events.append(ev)
                else:
                    events.append({**base, "event_type": "tool_invocation",
                                   "payload": {"mapped": False, "tool": name,
                                               "reason": "navigate_without_url"}})
            elif name in ("read_file", "terminal", "execute_code", "browser_snapshot",
                          "process", "search_files"):
                # support tools; only scanned later for citations, not navigation.
                events.append({**base, "event_type": "tool_invocation",
                               "payload": {"mapped": True, "tool": name,
                                           "class": "support_tool"}})
            elif name in ("browser_click", "browser_scroll", "browser_press",
                          "browser_type", "browser_back", "browser_vision",
                          "browser_console", "browser_get_images"):
                events.append({**base, "event_type": "tool_invocation",
                               "payload": {"mapped": True, "tool": name,
                                           "class": "browser_action"}})
            else:
                events.append({**base, "event_type": "tool_invocation",
                               "payload": {"mapped": False, "tool": name}})
        # --- tool outputs ---
        if msg["role"] == "tool":
            # find which assistant call this answers (nearest preceding call_id
            # is not stored on tool rows in this schema; we approximate by
            # attaching to the most recent unjoined search_query event).
            body = msg["content"] or ""
            urls_in_output = URL_RE.findall(body)[:50]
            joined = None
            for i in range(len(events) - 1, -1, -1):
                e = events[i]
                if e["event_type"] == "search_query" and "results_joined" not in e["payload"]:
                    joined = i
                    break
            if joined is not None and urls_in_output:
                events[joined]["payload"]["results_joined"] = True
                seen, ranked = set(), []
                rank = 1
                for u in urls_in_output:
                    u = u.rstrip(".,;:")
                    if u in seen:
                        continue
                    seen.add(u)
                    ranked.append({"rank": rank, "url": u, "domain": host_of(u)})
                    rank += 1
                events.append({
                    "seq": seq, "ts": msg["timestamp"],
                    "source_message_id": msg["id"],
                    "origin_session": msg.get("session_id"),
                    "event_type": "search_results",
                    "payload": {"query_ref_seq": events[joined]["seq"],
                                "results": ranked,
                                "extraction": "url_order_in_tool_output"},
                })
                seq += 1

    # --- citations + final choice from final assistant prose ---
    final_prose = ""
    msg_sid_of_final = None
    for msg in reversed(messages):
        if msg["role"] == "assistant" and (msg["content"] or "").strip():
            final_prose = msg["content"]
            msg_sid_of_final = msg.get("session_id")
            break
    cited = []
    seen = set()
    for u in URL_RE.findall(final_prose or ""):
        u = u.rstrip(".,;:")
        if u not in seen:
            seen.add(u)
            cited.append({"url": u, "where": "final_report"})
    if final_prose.strip():
        events.append({
            "seq": seq, "ts": None, "source_message_id": None,
            "origin_session": msg_sid_of_final,
            "event_type": "final_choice",
            "payload": {
                "report_excerpt": final_prose[:2000],
                "named_urls": [c["url"] for c in cited],
            },
        })
        seq += 1
    for c in cited:
        events.append({
            "seq": seq, "ts": None, "source_message_id": None,
            "origin_session": msg_sid_of_final,
            "event_type": "citation",
            "payload": dict(c),
        })
        seq += 1

    # citations appearing in tool outputs (dual-source rule §7)
    for msg in messages:
        if msg["role"] == "tool":
            for u in URL_RE.findall(msg["content"] or "")[:20]:
                u2 = u.rstrip(".,;:")
                events.append({
                    "seq": seq, "ts": msg["timestamp"],
                    "source_message_id": msg["id"],
                    "origin_session": msg.get("session_id"),
                    "event_type": "citation",
                    "payload": {"url": u2, "where": "tool_output"},
                })
                seq += 1

    events.sort(key=lambda e: e["seq"])
    return events


def cmd_extract(a):
    profile_home = f"/root/.hermes/profiles/{a.profile}"
    state_db = os.path.join(profile_home, "state.db")
    if not os.path.exists(state_db):
        print(f"ERROR: no state.db for profile {a.profile}: {state_db}",
              file=sys.stderr)
        return 2

    # --- attribution guard (added after batch-2 mis-attribution finding):
    # a trial session must be a top-level CLI session whose first user
    # message IS the frozen task prompt. Subagent sessions and foreign
    # workloads sharing the profile state.db must never be extracted.
    con = sqlite3.connect(f"file:{state_db}?mode=ro", uri=True)
    srow = con.execute("SELECT parent_session_id, source FROM sessions "
                       "WHERE id=?", (a.session,)).fetchone()
    con.close()
    if not srow:
        print(f"ERROR: unknown session {a.session} in {state_db}",
              file=sys.stderr)
        return 2
    if srow[0] is not None or srow[1] != "cli":
        print(f"ABORT: session {a.session} is not a top-level CLI session "
              f"(parent={srow[0]}, source={srow[1]!r}) — refusing to "
              f"extract a non-trial session", file=sys.stderr)
        return 4

    messages = load_session_messages(state_db, a.session)
    if not messages:
        print(f"ERROR: no messages for session {a.session} in {state_db}",
              file=sys.stderr)
        return 2
    first_user = next((m["content"] for m in messages
                       if m["role"] == "user"), "")
    if a.expect_prompt and first_user.strip() != a.expect_prompt.strip():
        print(f"ABORT: first user prompt of {a.session} does not match the "
              f"frozen task template — possible foreign/misattributed "
              f"session", file=sys.stderr)
        return 4

    events = extract_events(messages)
    first_ts = next((m["timestamp"] for m in messages if m["timestamp"]), None)
    last_ts = next((m["timestamp"] for m in reversed(messages)
                    if m["timestamp"]), None)

    counts = {}
    for e in events:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1

    child_sids = sorted({m["session_id"] for m in messages} - {a.session})
    trace = {
        "protocol_version": a.protocol_version,
        "extracted_at": now_iso(),
        "subject": {
            "harness": f"hermes --profile {a.profile} -z",
            "profile": a.profile,
            "provider": a.provider,
            "model": a.model,
            "session_id": a.session,
            "subagent_session_ids": child_sids,
        },
        "intent": {"intent_id": a.intent_id, "intent_hash": a.intent_hash},
        "network_environment": a.network_environment,
        "window": {"first_ts": first_ts, "last_ts": last_ts},
        "event_counts": counts,
        "events": events,
    }
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "trace_raw.json")
    with open(path, "w") as f:
        json.dump(trace, f, indent=1)
    print(f"wrote {path}")
    print("event_counts:", json.dumps(counts))
    return 0


def cmd_ingest(a):
    trace = json.load(open(os.path.join(a.trace, "trace_raw.json")))
    sid = trace["subject"]["session_id"]

    con = sqlite3.connect(a.db)
    cur = con.cursor()
    try:
        cur.execute("BEGIN")

        # idempotency guard: same session must never double-insert
        row = cur.execute(
            "SELECT trial_id FROM field_trials WHERE session_id=?",
            (sid,)).fetchone()
        if row:
            print(f"SKIP: session {sid} already ingested as {row[0]}")
            con.rollback()
            return 0

        intent = trace["intent"]
        # verify frozen intent exists and hash matches
        irow = cur.execute(
            "SELECT intent_hash FROM site_intents WHERE intent_id=?",
            (intent["intent_id"],)).fetchone()
        if not irow:
            print(f"ABORT: unknown intent {intent['intent_id']}", file=sys.stderr)
            con.rollback()
            return 3
        if a.verify_hash and irow[0] != intent["intent_hash"]:
            print("ABORT: intent_hash mismatch vs frozen row", file=sys.stderr)
            con.rollback()
            return 3

        counts = trace.get("event_counts", {})
        n_queries = counts.get("search_query", 0)
        final_ev = next((e for e in reversed(trace["events"])
                         if e["event_type"] == "final_choice"), None)
        named = (final_ev["payload"].get("named_urls") if final_ev else None) or []
        task_success = 1 if named else (0 if final_ev else None)

        trial_id = "ft_" + uuid.uuid4().hex[:12]
        subj = trace["subject"]
        cur.execute(
            """INSERT INTO field_trials
               (trial_id, intent_id, agent_model, agent_version, provider,
                session_id, started_at, completed_at, search_queries_json,
                final_action, task_success)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (trial_id, intent["intent_id"], subj["model"],
             trace.get("model_version") or subj["model"], subj["provider"],
             sid, trace["window"]["first_ts"], trace["window"]["last_ts"],
             json.dumps({"query_count": n_queries}),
             ("reported:" + (named[0] if named else "none")) if final_ev else None,
             task_success))

        for e in trace["events"]:
            if e["event_type"] == "search_query":
                qid = "sq_" + uuid.uuid4().hex[:12]
                cur.execute(
                    """INSERT INTO search_queries
                       (query_id, trial_id, query_text, query_order,
                        results_json, result_opened, reformulation)
                       VALUES (?,?,?,?,?,?,?)""",
                    (qid, trial_id, e["payload"].get("query", ""),
                     e["seq"], json.dumps(e["payload"]), None, None))

            obs_id = "obs_" + uuid.uuid4().hex[:12]
            et = e["event_type"]
            if et not in EVENT_TYPES_SCHEMA:
                et_mapped = "tool_invocation"
            else:
                et_mapped = et
            payload = dict(e.get("payload") or {})
            if et != et_mapped:
                payload["unmapped_from"] = et
            cur.execute(
                """INSERT INTO observations
                   (observation_id, experiment_id, intent_id, created_at,
                    evidence_tier, event_type, model_family, model_version,
                    provider, session_id, payload_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (obs_id, None, intent["intent_id"],
                 e.get("ts") and str(e["ts"]) or trace["extracted_at"],
                 "field", et_mapped, subj["model"],
                 trace.get("model_version") or subj["model"],
                 subj["provider"], sid, json.dumps(payload)))

        con.commit()
        print(f"INGESTED trial={trial_id} session={sid} "
              f"events={len(trace['events'])} queries={n_queries} "
              f"task_success={task_success}")
        return 0
    except Exception as ex:
        con.rollback()
        raise
    finally:
        con.close()


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("extract")
    pe.add_argument("--profile", required=True)
    pe.add_argument("--session", required=True)
    pe.add_argument("--intent-id", required=True)
    pe.add_argument("--intent-hash", required=True)
    pe.add_argument("--out", required=True)
    pe.add_argument("--provider", default="opencode-go")
    pe.add_argument("--model", default="mimo-v2.5")
    pe.add_argument("--network-environment", default="unknown")
    pe.add_argument("--protocol-version", default="field-v1")
    pe.add_argument("--expect-prompt", default=(
        "Find a domain availability API: a service that checks whether a "
        "domain name is available to register. Use your web search and "
        "browsing tools to find real services. When you have found one, "
        "report its name and URL."),
        help="exact first-user-prompt a trial session must carry "
             "(attribution guard; pass empty string to disable)")

    pi = sub.add_parser("ingest")
    pi.add_argument("--trace", required=True, help="dir containing trace_raw.json")
    pi.add_argument("--db", default="/root/agentseolab/lab.db")
    pi.add_argument("--verify-hash", action=argparse.BooleanOptionalAction,
                    default=True)

    a = p.parse_args()
    if a.cmd == "extract":
        sys.exit(cmd_extract(a))
    else:
        sys.exit(cmd_ingest(a))


if __name__ == "__main__":
    main()
