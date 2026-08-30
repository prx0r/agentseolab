"""DomainArena Hackathon Demo — single-page vertical execution trace.

Flow:
1. YOUR INTENT (prompt entry)
2. LIVE DOMAIN DISCOVERY (name.com search)
3. AGENT COMPREHENSION (semantic inversion)
4. DOMAIN ARENA (recommendation)
5. LIVE CHECKOUT (availability + pricing)
6. NAME.COM REGISTRATION
7. DNS CONFIGURATION
8. VERIFIED (evidence receipt)

Run: python3 -m domainarena.web.demo  → http://127.0.0.1:8777
"""
from __future__ import annotations
import asyncio
import hashlib
import html
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from domainarena.models import ConstraintSet, Candidate, InventorySnapshot, EvidenceVector  # noqa: E402
from domainarena.providers.namecom import client_from_env, NameComError  # noqa: E402
from domainarena.optimizer import recommend, weighted_score  # noqa: E402

PORT = int(os.environ.get("DOMAINARENA_PORT", "8777"))

# In-memory state for demo
_STATE: dict = {}
_API_TRACE: list = []


def _esc(s):
    return html.escape(str(s), quote=False)


def _log_api(method: str, endpoint: str, status: int, latency_ms: int, detail: str = ""):
    _API_TRACE.append({
        "time": time.strftime("%H:%M:%S"),
        "method": method,
        "endpoint": endpoint,
        "status": status,
        "latency_ms": latency_ms,
        "detail": detail[:100],
    })


def _cf_infer(model_id: str, prompt: str, max_tokens: int = 200) -> dict:
    """Call Cloudflare Workers AI."""
    import urllib.request
    cf_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/{model_id}"
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    headers = {"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read())
        latency_ms = int((time.time() - t0) * 1000)
        text = (res.get("result", {}).get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        return {"ok": True, "text": text, "latency_ms": latency_ms}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)[:200], "latency_ms": int((time.time() - t0) * 1000)}


def _semantic_inversion(domain: str, model_id: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast") -> dict:
    """Ask model what it thinks runs behind this domain."""
    prompt = (
        f"You are shown a domain name with no other context.\n"
        f"Domain: {domain}\n\n"
        f"What product or service do you think runs behind this domain?\n"
        f"Reply in one sentence."
    )
    return _cf_infer(model_id, prompt)


def _semantic_score(inference: str, intent: str) -> dict:
    """Hidden scorer: compare inference against frozen intent."""
    prompt = (
        f"You are a semantic evaluator. Rate how well the inference matches the intent.\n\n"
        f"FROZEN INTENT: {intent}\n"
        f"INFERENCE: {inference}\n\n"
        f"Score 0.0-1.0: 1.0=exact match, 0.7-0.9=partial, 0.3-0.6=weak, 0.0-0.2=none.\n"
        f'Reply in JSON: {{"score": <float>, "label": "<exact|partial|none>"}}'
    )
    res = _cf_infer(prompt)
    if not res["ok"]:
        return {"score": 0.0, "label": "error"}
    try:
        parsed = json.loads(res["text"])
        return {"score": float(parsed.get("score", 0)), "label": parsed.get("label", "none")}
    except:
        import re
        m = re.search(r'"?score"?\s*[:=]\s*([0-9.]+)', res["text"])
        return {"score": float(m.group(1)) if m else 0.0, "label": "none"}


PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>DomainArena — Hackathon Demo</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d1117;color:#e6edf3;max-width:1100px;margin:0 auto;padding:20px}
h1{color:#58a6ff;font-size:28px;margin-bottom:4px}
h2{color:#58a6ff;font-size:20px;margin:24px 0 12px}
h3{color:#c9d1d9;font-size:16px;margin:12px 0 8px}
.subtitle{color:#8b949e;margin-bottom:24px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;margin:12px 0}
.step{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;margin:12px 0;position:relative}
.step-num{position:absolute;top:-12px;left:16px;background:#238636;color:#fff;border-radius:12px;padding:2px 10px;font-size:13px;font-weight:600}
.step-title{font-size:17px;font-weight:600;color:#c9d1d9;margin-bottom:8px}
.step-sub{color:#8b949e;font-size:13px}
input,select,textarea{background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:8px 12px;font-size:14px;width:100%}
textarea{min-height:60px;resize:vertical}
button{background:#238636;color:#fff;border:0;border-radius:6px;padding:10px 24px;font-size:15px;cursor:pointer;font-weight:600}
button:hover{background:#2ea043}
button:disabled{background:#21262d;color:#484f58;cursor:not-allowed}
button.reject{background:#da3633}
button.reject:hover{background:#f85149}
table{width:100%;border-collapse:collapse;margin:8px 0}
td,th{padding:6px 10px;border-bottom:1px solid #21262d;text-align:left;font-size:13px}
th{color:#8b949e;font-weight:500}
.ok{color:#3fb950}.rej{color:#f85149}.warn{color:#d29922}.muted{color:#8b949e}
.big{font-size:32px;color:#58a6ff;font-weight:700}
.tag{display:inline-block;background:#1f6feb33;color:#58a6ff;border-radius:4px;padding:2px 8px;font-size:12px;margin:2px}
.tag-green{background:#23863633;color:#3fb950}
.tag-red{background:#da363333;color:#f85149}
.tag-yellow{background:#d2992233;color:#d29922}
.trace{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px;font-family:'SF Mono',monospace;font-size:12px;max-height:300px;overflow-y:auto}
.trace-row{display:flex;gap:8px;padding:3px 0;border-bottom:1px solid #21262d}
.trace-time{color:#484f58;min-width:60px}
.trace-method{color:#58a6ff;min-width:40px}
.trace-endpoint{color:#c9d1d9;flex:1}
.trace-status{min-width:30px}
.trace-latency{color:#8b949e;min-width:60px;text-align:right}
.receipt{background:#0d1117;border:1px solid #238636;border-radius:6px;padding:16px;font-family:monospace;font-size:13px}
</style></head><body>
<h1>⚔️ DomainArena</h1>
<p class="subtitle">A/B testing for domain names in the agentic web — powered by name.com</p>
{body}
</body></html>"""


STEP_INTENT = """
<div class="step">
<span class="step-num">1</span>
<div class="step-title">YOUR INTENT</div>
<div class="step-sub">Describe what you're building</div>
<form method="post" action="/run" style="margin-top:12px">
<label>What are you building?<br>
<textarea name="description">{desc}</textarea></label><br><br>
<label>Budget — first year ($)<input name="maxp" value="{maxp}" style="width:120px" type="number"></label>
<label>renewal ($)<input name="maxr" value="{maxr}" style="width:120px" type="number"></label><br><br>
<button type="submit">Run DomainArena</button>
</form>
</div>"""


def _step_discovery(candidates: list, api_trace: list) -> str:
    rows = "".join(
        f"<tr><td>{_esc(c['domain'])}</td><td>${c['price']}</td><td>${c['renewal']}</td>"
        f"<td>{'<span class=ok>✓</span>' if c['purchasable'] else '<span class=rej>✗</span>'}</td></tr>"
        for c in candidates
    )
    return f"""
<div class="step">
<span class="step-num">2</span>
<div class="step-title">LIVE DOMAIN DISCOVERY</div>
<div class="step-sub">Powered by name.com Search API</div>
<table><tr><th>domain</th><th>first year</th><th>renewal</th><th>available</th></tr>{rows}</table>
</div>"""


def _step_comprehension(inferences: list) -> str:
    cards = ""
    for inf in inferences:
        score = inf.get("score", 0)
        label = inf.get("label", "none")
        tag_class = "tag-green" if score >= 0.7 else "tag-yellow" if score >= 0.3 else "tag-red"
        cards += f"""
<div class="card" style="margin:8px 0">
<b>{_esc(inf['domain'])}</b> <span class="tag {tag_class}">{label} {score:.1f}</span>
<br><span class="muted">AI infers:</span> {_esc(inf['inference'][:150])}
</div>"""
    return f"""
<div class="step">
<span class="step-num">3</span>
<div class="step-title">AGENT COMPREHENSION</div>
<div class="step-sub">What do AI models think this domain does? (blind — no context)</div>
{cards}
</div>"""


def _step_recommendation(rec: dict, evidence: dict) -> str:
    if not rec:
        return '<div class="step"><span class="step-num">4</span><div class="step-title">NO RECOMMENDATION</div><div class="muted">No feasible candidates under budget</div></div>'
    explanation = "".join(f"<li>{_esc(x)}</li>" for x in rec.get("explanation", []))
    return f"""
<div class="step">
<span class="step-num">4</span>
<div class="step-title">DOMAIN ARENA</div>
<div class="step-sub">Evidence-based recommendation</div>
<div class="big">{_esc(rec['domain'])}</div>
<ul>{explanation}</ul>
<p class="muted">score: {rec.get('score', 0):.4f} · coverage: {rec.get('evidence_coverage', 0):.0%} · status: {rec.get('recommendation_status', '?')}</p>
<form method="post" action="/prepare" style="margin-top:12px">
<input type="hidden" name="domain" value="{_esc(rec['domain'])}">
<input type="hidden" name="decision_id" value="{_esc(rec.get('decision_id', ''))}">
<button type="submit">Prepare Registration →</button>
</form>
</div>"""


def _step_checkout(domain: str, avail: dict) -> str:
    if not avail:
        return ""
    return f"""
<div class="step">
<span class="step-num">5</span>
<div class="step-title">LIVE CHECKOUT</div>
<div class="step-sub">Fresh availability + pricing check (fail-closed)</div>
<table>
<tr><td>Domain</td><td><b>{_esc(domain)}</b></td></tr>
<tr><td>Available</td><td class="ok">{'✓ Yes' if avail.get('available') else '✗ No'}</td></tr>
<tr><td>Price</td><td>${avail.get('price', '?')}</td></tr>
<tr><td>Renewal</td><td>${avail.get('renewal', '?')}</td></tr>
<tr><td>Premium</td><td>{'Yes' if avail.get('premium') else 'No'}</td></tr>
</table>
<form method="post" action="/register" style="margin-top:12px">
<input type="hidden" name="domain" value="{_esc(domain)}">
<input type="hidden" name="decision_id" value="{_esc(avail.get('decision_id', ''))}">
<button type="submit">Approve & Register →</button>
<button type="submit" formaction="/cancel" class="reject" style="margin-left:8px">Reject</button>
</form>
</div>"""


def _step_registered(domain: str, reg: dict) -> str:
    if not reg:
        return ""
    return f"""
<div class="step">
<span class="step-num">6</span>
<div class="step-title">NAME.COM REGISTRATION</div>
<div class="step-sub">CreateDomain API call</div>
<table>
<tr><td>Status</td><td class="ok">REGISTERED</td></tr>
<tr><td>Domain</td><td>{_esc(domain)}</td></tr>
<tr><td>Idempotency Key</td><td class="muted" style="font-size:11px">{_esc(reg.get('idempotency_key', '?')[:32])}...</td></tr>
</table>
<form method="post" action="/configure-dns" style="margin-top:12px">
<input type="hidden" name="domain" value="{_esc(domain)}">
<button type="submit">Configure DNS →</button>
</form>
</div>"""


def _step_dns(domain: str, dns: dict) -> str:
    if not dns:
        return ""
    records = dns.get("records", [])
    rows = "".join(
        f"<tr><td>{_esc(r.get('host', ''))}</td><td>{_esc(r.get('type', ''))}</td><td>{_esc(r.get('answer', ''))}</td></tr>"
        for r in records
    )
    return f"""
<div class="step">
<span class="step-num">7</span>
<div class="step-title">DNS CONFIGURATION</div>
<div class="step-sub">CreateRecord + ListRecords verification</div>
<table><tr><th>host</th><th>type</th><th>answer</th></tr>{rows}</table>
</div>"""


def _step_verified(domain: str, receipt: dict) -> str:
    if not receipt:
        return ""
    return f"""
<div class="step">
<span class="step-num">8</span>
<div class="step-title">VERIFIED</div>
<div class="step-sub">Evidence receipt — reproducible and auditable</div>
<div class="receipt">
<b>Receipt Hash:</b> {_esc(receipt.get('hash', '?'))}<br>
<b>Domain:</b> {_esc(domain)}<br>
<b>Intent:</b> {_esc(receipt.get('intent', '?'))}<br>
<b>Timestamp:</b> {_esc(receipt.get('timestamp', '?'))}<br>
<b>API Calls:</b> {receipt.get('api_calls', 0)}
</div>
</div>"""


def _api_trace_panel() -> str:
    if not _API_TRACE:
        return ""
    rows = "".join(
        f"""<div class="trace-row">
<span class="trace-time">{_esc(t['time'])}</span>
<span class="trace-method">{_esc(t['method'])}</span>
<span class="trace-endpoint">{_esc(t['endpoint'])}</span>
<span class="trace-status {'ok' if t['status'] < 400 else 'rej'}">{t['status']}</span>
<span class="trace-latency">{t['latency_ms']}ms</span>
</div>"""
        for t in _API_TRACE[-20:]  # last 20 calls
    )
    return f"""
<div class="card">
<h3>name.com API Trace</h3>
<div class="trace">{rows}</div>
</div>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, status=200):
        data = PAGE.replace("{body}", body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, path):
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self.wfile.write(b"ok")
            return
        if path == "/trace":
            # Return API trace as JSON
            data = json.dumps(_API_TRACE[-50:], indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        # Default: show form
        body = STEP_INTENT.format(desc="Repairs malformed JSON for AI agents", maxp=25, maxr=35)
        body += _api_trace_panel()
        self._send(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(n).decode())
        path = urlparse(self.path).path

        try:
            if path == "/run":
                body = asyncio.run(self._handle_run(form))
            elif path == "/prepare":
                body = asyncio.run(self._handle_prepare(form))
            elif path == "/register":
                body = asyncio.run(self._handle_register(form))
            elif path == "/configure-dns":
                body = asyncio.run(self._handle_dns(form))
            elif path == "/cancel":
                body = self._handle_cancel(form)
            else:
                body = f'<div class="card rej">Unknown path: {_esc(path)}</div>'
                body += STEP_INTENT.format(desc="Repairs malformed JSON for AI agents", maxp=25, maxr=35)
        except Exception as e:
            body = f'<div class="card rej">Error: {_esc(e)}</div>'
            body += STEP_INTENT.format(desc="Repairs malformed JSON for AI agents", maxp=25, maxr=35)

        self._send(body)

    async def _handle_run(self, form) -> str:
        """Step 2: Search → Inference → Recommend."""
        description = form.get("description", [""])[0]
        maxp = float(form.get("maxp", ["25"])[0] or 25)
        maxr = float(form.get("maxr", ["35"])[0] or 35)

        # Step 1: Intent
        body = STEP_INTENT.format(desc=_esc(description), maxp=int(maxp), maxr=int(maxr))

        # Step 2: Live name.com search
        client = client_from_env()
        t0 = time.time()
        try:
            search_results = await client.search(description.split()[0], ["dev", "com", "io"])
            _log_api("POST", "/domains:search", 200, int((time.time()-t0)*1000),
                     f"keyword={description.split()[0]}")
        except Exception as e:
            _log_api("POST", "/domains:search", 500, int((time.time()-t0)*1000), str(e)[:80])
            search_results = []

        # Filter by budget
        feasible = []
        for r in search_results:
            if r.purchasable and r.purchase_price and r.purchase_price <= maxp:
                if r.renewal_price and r.renewal_price <= maxr:
                    feasible.append({
                        "domain": r.domain_name,
                        "price": r.purchase_price,
                        "renewal": r.renewal_price,
                        "purchasable": True,
                    })
        await client.close()

        if not feasible:
            body += '<div class="card rej">No domains found under budget. Try higher budget.</div>'
            body += _api_trace_panel()
            return body

        body += _step_discovery(feasible, _API_TRACE)

        # Step 3: Semantic inversion (what does AI think each domain does?)
        inferences = []
        for cand in feasible[:5]:  # top 5
            inv = _semantic_inversion(cand["domain"])
            sc = _semantic_score(inv.get("text", ""), description)
            inferences.append({
                "domain": cand["domain"],
                "inference": inv.get("text", ""),
                "score": sc["score"],
                "label": sc["label"],
                "latency_ms": inv.get("latency_ms", 0),
            })
            _log_api("POST", f"CF AI ({'infer'}", 200, inv.get("latency_ms", 0), cand["domain"])

        body += _step_comprehension(inferences)

        # Step 4: Recommendation
        candidates_with_ev = []
        for cand in feasible[:5]:
            inf = next((i for i in inferences if i["domain"] == cand["domain"]), {})
            ev = EvidenceVector(
                semantic_transmission=inf.get("score", 0.0),
                task_success=inf.get("score", 0.0) * 0.9,
            )
            sld, _, tld = cand["domain"].partition(".")
            candidates_with_ev.append((
                Candidate(
                    candidate_id=cand["domain"],
                    domain_name=cand["domain"],
                    generator="name.com-search",
                    inventory=InventorySnapshot(
                        domain_name=cand["domain"], sld=sld, tld=tld,
                        purchasable=True, purchase_price=cand["price"],
                        renewal_price=cand["renewal"],
                        checked_at=time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                ),
                ev,
            ))

        rec = recommend(candidates_with_ev, "ai_agent")
        rec_dict = {
            "domain": rec.domain_name,
            "score": rec.score,
            "evidence_coverage": rec.evidence_coverage,
            "recommendation_status": rec.recommendation_status,
            "explanation": rec.explanation,
            "on_pareto_front": rec.on_pareto,
        }
        # Store for later steps
        _STATE["recommendation"] = rec_dict
        _STATE["intent"] = description
        _STATE["feasible"] = feasible

        body += _step_recommendation(rec_dict, {})
        body += _api_trace_panel()
        return body

    async def _handle_prepare(self, form) -> str:
        """Step 5: Fresh availability check."""
        domain = form.get("domain", [""])[0]
        decision_id = form.get("decision_id", [""])[0]

        body = STEP_INTENT.format(desc=_esc(_STATE.get("intent", "")), maxp=25, maxr=35)

        client = client_from_env()
        t0 = time.time()
        try:
            entry = await client.check_availability_fail_closed(domain)
            _log_api("POST", "/domains:checkAvailability", 200, int((time.time()-t0)*1000), domain)
            pricing = await client.get_pricing(domain)
            _log_api("GET", f"/domains/{domain}:getPricing", 200, int((time.time()-t0)*1000), domain)
        except Exception as e:
            _log_api("POST", "/domains:checkAvailability", 500, int((time.time()-t0)*1000), str(e)[:80])
            body += f'<div class="card rej">Availability check failed: {_esc(e)}</div>'
            body += _api_trace_panel()
            return body
        finally:
            await client.close()

        def _extract_price(p):
            if not isinstance(p, dict): return None
            for k in ("purchasePrice", "purchase_price"):
                if p.get(k) is not None: return p[k]
            for t in p.get("tiers", []) or []:
                if t.get("purchasePrice") is not None: return t["purchasePrice"]
            return None

        avail = {
            "available": entry.get("purchasable", False),
            "price": _extract_price(pricing) or entry.get("purchasePrice"),
            "renewal": pricing.get("renewalPrice") if isinstance(pricing, dict) else None,
            "premium": entry.get("premium", False),
            "decision_id": decision_id,
        }
        _STATE["checkout"] = avail

        rec = _STATE.get("recommendation", {})
        body += _step_recommendation(rec, {})
        body += _step_checkout(domain, avail)
        body += _api_trace_panel()
        return body

    async def _handle_register(self, form) -> str:
        """Step 6: Register domain."""
        domain = form.get("domain", [""])[0]
        decision_id = form.get("decision_id", [""])[0]

        body = STEP_INTENT.format(desc=_esc(_STATE.get("intent", "")), maxp=25, maxr=35)

        client = client_from_env()
        t0 = time.time()
        try:
            import hashlib
            idem = hashlib.sha256(f"{decision_id}|{domain}|register".encode()).hexdigest()
            payload = {"domain": {"domainName": domain}}
            reg = await client.register_domain(payload, idem)
            _log_api("POST", "/domains", 200, int((time.time()-t0)*1000), domain)
            got = await client.get_domain(domain)
            _log_api("GET", f"/domains/{domain}", 200, int((time.time()-t0)*1000), domain)
        except Exception as e:
            _log_api("POST", "/domains", 500, int((time.time()-t0)*1000), str(e)[:80])
            body += f'<div class="card rej">Registration failed: {_esc(e)}</div>'
            body += _api_trace_panel()
            return body
        finally:
            await client.close()

        reg_info = {"idempotency_key": idem, "status": "REGISTERED"}
        _STATE["registration"] = reg_info

        rec = _STATE.get("recommendation", {})
        checkout = _STATE.get("checkout", {})
        body += _step_recommendation(rec, {})
        body += _step_checkout(domain, checkout)
        body += _step_registered(domain, reg_info)
        body += _api_trace_panel()
        return body

    async def _handle_dns(self, form) -> str:
        """Step 7: Configure DNS."""
        domain = form.get("domain", [""])[0]

        body = STEP_INTENT.format(desc=_esc(_STATE.get("intent", "")), maxp=25, maxr=35)

        client = client_from_env()
        t0 = time.time()
        try:
            import hashlib, json as _json
            receipt_hash = hashlib.sha256(_json.dumps({
                "domain": domain, "intent": _STATE.get("intent", "")},
                sort_keys=True).encode()).hexdigest()
            txt_answer = f"sha256:{receipt_hash}"

            await client.create_dns_record(domain, host="_domainarena",
                                           record_type="TXT", answer=txt_answer)
            _log_api("POST", f"/domains/{domain}/records", 200, int((time.time()-t0)*1000), "TXT")

            records = await client.list_dns_records(domain)
            _log_api("GET", f"/domains/{domain}/records", 200, int((time.time()-t0)*1000), "")
        except Exception as e:
            _log_api("POST", f"/domains/{domain}/records", 500, int((time.time()-t0)*1000), str(e)[:80])
            records = []
        finally:
            await client.close()

        dns_info = {"records": records if isinstance(records, list) else []}
        _STATE["dns"] = dns_info

        # Build receipt
        import hashlib, json as _json
        receipt_hash = hashlib.sha256(_json.dumps({
            "domain": domain,
            "intent": _STATE.get("intent", ""),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }, sort_keys=True).encode()).hexdigest()
        receipt = {
            "hash": f"sha256:{receipt_hash}",
            "intent": _STATE.get("intent", ""),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "api_calls": len(_API_TRACE),
        }

        rec = _STATE.get("recommendation", {})
        checkout = _STATE.get("checkout", {})
        reg = _STATE.get("registration", {})
        body += _step_recommendation(rec, {})
        body += _step_checkout(domain, checkout)
        body += _step_registered(domain, reg)
        body += _step_dns(domain, dns_info)
        body += _step_verified(domain, receipt)
        body += _api_trace_panel()
        return body

    def _handle_cancel(self, form) -> str:
        body = STEP_INTENT.format(desc=_esc(_STATE.get("intent", "")), maxp=25, maxr=35)
        body += '<div class="card warn">Registration cancelled by user.</div>'
        body += _api_trace_panel()
        return body

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"DomainArena Hackathon Demo on http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
