"""DomainArena Hackathon Demo — calls DomainService directly.

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

from domainarena.models import ConstraintSet  # noqa: E402
from domainarena.service import get_service, DecisionStatus  # noqa: E402

PORT = int(os.environ.get("DOMAINARENA_PORT", "8777"))

# In-memory state for demo flow
_STATE: dict = {}


def _esc(s):
    return html.escape(str(s), quote=False)


def _cf_infer(model_id: str, prompt: str, max_tokens: int = 200) -> dict:
    """Call Cloudflare Workers AI."""
    import urllib.request
    cf_account = (os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
                  or os.environ.get("CF_ACCOUNT_ID", ""))
    cf_token = (os.environ.get("CLOUDFLARE_API_TOKEN", "")
                or os.environ.get("CF_TOKEN", ""))
    if not cf_account or not cf_token:
        return {"ok": False, "text": "", "error": "no credentials", "latency_ms": 0}
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


def _semantic_inversion(domain: str) -> dict:
    """Ask model what it thinks runs behind this domain."""
    model_id = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    prompt = (
        f"You are shown a domain name with no other context.\n"
        f"Domain: {domain}\n\n"
        f"What product or service do you think runs behind this domain?\n"
        f"Reply in one sentence."
    )
    return _cf_infer(model_id, prompt)


def _semantic_score(inference: str, intent: str) -> dict:
    """Hidden scorer: compare inference against frozen intent.
    Uses a DIFFERENT model than the tested model (generator/judge separation)."""
    model_id = "@cf/mistralai/mistral-small-3.1-24b-instruct"
    prompt = (
        f"You are a semantic evaluator. Rate how well the inference matches the intent.\n\n"
        f"FROZEN INTENT: {intent}\n"
        f"INFERENCE: {inference}\n\n"
        f"Score 0.0-1.0: 1.0=exact match, 0.7-0.9=partial, 0.3-0.6=weak, 0.0-0.2=none.\n"
        f'Reply in JSON: {{"score": <float>, "label": "<exact|partial|none>"}}'
    )
    res = _cf_infer(model_id, prompt)
    if not res["ok"]:
        return {"score": 0.0, "label": "error", "evidence_status": "NOT_MEASURED"}
    try:
        parsed = json.loads(res["text"])
        return {"score": float(parsed.get("score", 0)),
                "label": parsed.get("label", "none"),
                "evidence_status": "MEASURED"}
    except Exception:
        import re
        m = re.search(r'"?score"?\s*[:=]\s*([0-9.]+)', res["text"])
        return {"score": float(m.group(1)) if m else 0.0,
                "label": "none",
                "evidence_status": "MEASURED"}


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
.status-badge{display:inline-block;border-radius:4px;padding:2px 8px;font-size:12px;font-weight:600}
.status-RECOMMENDED{background:#1f6feb33;color:#58a6ff}
.status-PREPARED{background:#d2992233;color:#d29922}
.status-APPROVED{background:#23863633;color:#3fb950}
.status-REGISTERED{background:#23863633;color:#3fb950}
.status-VERIFIED{background:#23863633;color:#3fb950}
.status-UNAVAILABLE{background:#da363333;color:#f85149}
.status-ERROR{background:#da363333;color:#f85149}
</style></head><body>
<h1>DomainArena</h1>
<p class="subtitle">A/B testing for domain names in the agentic web — powered by name.com</p>
{body}
</body></html>"""


STEP_INTENT = """
<div class="step">
<span class="step-num">1</span>
<div class="step-title">YOUR INTENT</div>
<div class="step-sub">MCP tool: <code>recommend_domain</code> — Describe what you're building</div>
<form method="post" action="/run" style="margin-top:12px">
<label>What are you building?<br>
<textarea name="description">{desc}</textarea></label><br><br>
<label>Budget — first year ($)<input name="maxp" value="{maxp}" style="width:120px" type="number"></label>
<label>renewal ($)<input name="maxr" value="{maxr}" style="width:120px" type="number"></label><br><br>
<button type="submit">Run DomainArena</button>
</form>
</div>"""


def _step_discovery(candidates: list, source: str = "fixture") -> str:
    rows = "".join(
        f"<tr><td>{_esc(c['domain'])}</td><td>${c.get('price', '?')}</td>"
        f"<td>{'<span class=ok>✓</span>' if c.get('available') else '<span class=rej>✗</span>'}</td></tr>"
        for c in candidates
    )
    if source == "live":
        title = "LIVE DOMAIN DISCOVERY"
        sub = f"MCP tool: <code>search_domain</code> — name.com Search API — {len(candidates)} candidates found"
        tag = '<span class="tag tag-green">LIVE</span>'
    else:
        title = "DOMAIN DISCOVERY (DEMO)"
        sub = f"MCP tool: <code>search_domain</code> — Fixture candidates — {len(candidates)} seed domains"
        tag = '<span class="tag tag-yellow">FIXTURE</span>'
    return f"""
<div class="step">
<span class="step-num">2</span>
<div class="step-title">{title} {tag}</div>
<div class="step-sub">{sub}</div>
<table><tr><th>domain</th><th>first year</th><th>available</th></tr>{rows}</table>
</div>"""


def _step_comprehension(inferences: list) -> str:
    cards = ""
    for inf in inferences:
        score = inf.get("score", 0)
        label = inf.get("label", "none")
        status = inf.get("evidence_status", "NOT_MEASURED")
        tag_class = "tag-green" if score >= 0.7 else "tag-yellow" if score >= 0.3 else "tag-red"
        status_tag = f'<span class="tag tag-green">{status}</span>' if status == "MEASURED" else f'<span class="tag tag-red">{status}</span>'
        cards += f"""
<div class="card" style="margin:8px 0">
<b>{_esc(inf['domain'])}</b> <span class="tag {tag_class}">{label} {score:.1f}</span> {status_tag}
<br><span class="muted">AI infers:</span> {_esc(inf['inference'][:150])}
</div>"""
    return f"""
<div class="step">
<span class="step-num">3</span>
<div class="step-title">AGENT COMPREHENSION</div>
<div class="step-sub">MCP tool: <code>compare_domains</code> — What do AI models think this domain does? (blind — no context)</div>
{cards}
</div>"""


def _step_recommendation(rec: dict) -> str:
    if not rec:
        return '<div class="step"><span class="step-num">4</span><div class="step-title">NO RECOMMENDATION</div></div>'
    status_class = f"status-{rec.get('status', 'RECOMMENDED')}"
    return f"""
<div class="step">
<span class="step-num">4</span>
<div class="step-title">DOMAIN ARENA</div>
<div class="step-sub">MCP tool: <code>recommend_domain</code> — Evidence-based recommendation</div>
<div class="big">{_esc(rec['domain'])}</div>
<p>Status: <span class="status-badge {status_class}">{rec.get('status', '?')}</span></p>
<p class="muted">decision_id: {_esc(rec.get('decision_id', '')[:20])}...</p>
<form method="post" action="/prepare" style="margin-top:12px">
<input type="hidden" name="decision_id" value="{_esc(rec.get('decision_id', ''))}">
<button type="submit">Prepare Registration →</button>
</form>
</div>"""


def _step_checkout(domain: str, prep: dict) -> str:
    if not prep:
        return ""
    status_class = f"status-{prep.get('status', 'PREPARED')}"
    return f"""
<div class="step">
<span class="step-num">5</span>
<div class="step-title">LIVE CHECKOUT</div>
<div class="step-sub">MCP tool: <code>prepare_registration</code> — Fresh availability + pricing check (fail-closed)</div>
<table>
<tr><td>Domain</td><td><b>{_esc(domain)}</b></td></tr>
<tr><td>Available</td><td class="ok">{'✓ Yes' if prep.get('purchasable') else '✗ No'}</td></tr>
<tr><td>Price</td><td>${prep.get('purchase_price', '?')}</td></tr>
<tr><td>Renewal</td><td>${prep.get('renewal_price', '?')}</td></tr>
<tr><td>Status</td><td><span class="status-badge {status_class}">{prep.get('status', '?')}</span></td></tr>
</table>
<form method="post" action="/approve" style="margin-top:12px">
<input type="hidden" name="decision_id" value="{_esc(prep.get('decision_id', ''))}">
<button type="submit">Approve & Register →</button>
<button type="submit" formaction="/reject" class="reject" style="margin-left:8px">Reject</button>
</form>
</div>"""


def _step_registered(domain: str, reg: dict) -> str:
    if not reg:
        return ""
    return f"""
<div class="step">
<span class="step-num">6</span>
<div class="step-title">NAME.COM REGISTRATION</div>
<div class="step-sub">MCP tool: <code>register_domain</code> — CreateDomain API — idempotent</div>
<table>
<tr><td>Status</td><td class="ok">REGISTERED</td></tr>
<tr><td>Domain</td><td>{_esc(domain)}</td></tr>
<tr><td>Idempotency Key</td><td class="muted" style="font-size:11px">{_esc(reg.get('idempotency_key', '?')[:32])}...</td></tr>
</table>
<form method="post" action="/configure-dns" style="margin-top:12px">
<input type="hidden" name="decision_id" value="{_esc(reg.get('decision_id', ''))}">
<button type="submit">Configure DNS →</button>
</form>
</div>"""


def _step_dns(domain: str, dns: dict) -> str:
    if not dns:
        return ""
    status_class = f"status-{dns.get('status', 'DNS_CONFIGURED')}"
    verified = dns.get("dns_receipt_verified", False)
    return f"""
<div class="step">
<span class="step-num">7</span>
<div class="step-title">DNS CONFIGURATION</div>
<div class="step-sub">MCP tool: <code>configure_dns</code> — CreateRecord + ListRecords verification</div>
<table>
<tr><td>Receipt Hash</td><td class="muted" style="font-size:11px">{_esc(dns.get('receipt_hash', '?')[:40])}...</td></tr>
<tr><td>Verified</td><td>{'✓ Yes' if verified else '✗ Pending'}</td></tr>
<tr><td>Status</td><td><span class="status-badge {status_class}">{dns.get('status', '?')}</span></td></tr>
</table>
</div>"""


def _step_verified(domain: str, verif: dict) -> str:
    if not verif:
        return ""
    return f"""
<div class="step">
<span class="step-num">8</span>
<div class="step-title">VERIFIED</div>
<div class="step-sub">MCP resource: <code>domainarena://decisions</code> — Evidence receipt — content-addressed, auditable</div>
<div class="receipt">
<b>Receipt Hash:</b> {_esc(verif.get('receipt_hash', '?'))}<br>
<b>Domain:</b> {_esc(domain)}<br>
<b>Status:</b> <span class="ok">VERIFIED</span>
</div>
</div>"""


def _api_trace_panel(trace: list) -> str:
    if not trace:
        return ""
    rows = "".join(
        f"""<div class="trace-row">
<span class="trace-time">{_esc(t['time'])}</span>
<span class="trace-method">{_esc(t['method'])}</span>
<span class="trace-endpoint">{_esc(t['endpoint'])}</span>
<span class="trace-status {'ok' if t['status'] < 400 else 'rej'}">{t['status']}</span>
<span class="trace-latency">{t['latency_ms']}ms</span>
</div>"""
        for t in trace[-20:]
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
        if path == "/":
            body = STEP_INTENT.format(
                desc=_STATE.get("description", "A JSON repair tool for fixing malformed JSON"),
                maxp=_STATE.get("maxp", "25"),
                maxr=_STATE.get("maxr", "35"),
            )
            self._send(body)
            return
        self._send("Not found", 404)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = parse_qs(self.rfile.read(length).decode())

        if path == "/run":
            self._handle_run(body)
        elif path == "/prepare":
            self._handle_prepare(body)
        elif path == "/approve":
            self._handle_approve(body)
        elif path == "/reject":
            self._handle_reject(body)
        elif path == "/configure-dns":
            self._handle_configure_dns(body)
        else:
            self._send("Not found", 404)

    def _handle_run(self, body: dict):
        """Run the full recommendation pipeline via DomainService."""
        desc = body.get("description", [""])[0]
        maxp = body.get("maxp", ["25"])[0]
        maxr = body.get("maxr", ["35"])[0]
        _STATE["description"] = desc
        _STATE["maxp"] = maxp
        _STATE["maxr"] = maxr

        svc = get_service()
        constraints = ConstraintSet(
            max_purchase_price=float(maxp) if maxp else None,
            max_renewal_price=float(maxr) if maxr else None,
        )

        # Determine mode: live if credentials present, else fixture
        mode = "live" if os.environ.get("NAMECOM_USERNAME") else "fixture"

        try:
            import asyncio
            ds, cands = asyncio.run(svc.recommend_async(
                description=desc,
                primary_job=desc,
                audience="ai_agent",
                constraints=constraints,
                mode=mode,
            ))
        except ValueError as e:
            self._send(f"<h1>Error</h1><p>{_esc(str(e))}</p>", 400)
            return

        # Build candidate list for display
        cand_display = [
            {"domain": c.domain_name, "price": c.inventory.purchase_price,
             "available": c.inventory.purchasable}
            for c, _ in cands
        ]

        # Run semantic inversion on top candidates (different model for scorer)
        inferences = []
        for c in cands[:3]:
            inv = _semantic_inversion(c.domain_name)
            score_result = _semantic_score(inv.get("text", ""), desc)
            inferences.append({
                "domain": c.domain_name,
                "inference": inv.get("text", ""),
                "score": score_result["score"],
                "label": score_result["label"],
                "evidence_status": score_result["evidence_status"],
                "latency_ms": inv.get("latency_ms", 0),
            })

        _STATE["decision_id"] = ds.decision_id
        _STATE["inferences"] = inferences
        _STATE["source"] = "name.com-live" if mode == "live" else "demo-fixture"

        # Build page
        body_html = ""
        body_html += STEP_INTENT.format(desc=desc, maxp=maxp, maxr=maxr)
        body_html += _step_discovery(cand_display, source=mode)
        body_html += _step_comprehension(inferences)
        body_html += _step_recommendation({
            "domain": ds.recommended_domain,
            "decision_id": ds.decision_id,
            "status": ds.status.value,
        })

        self._send(body_html)

    def _handle_prepare(self, body: dict):
        """Prepare registration via DomainService."""
        decision_id = body.get("decision_id", [""])[0]
        svc = get_service()

        try:
            prep = svc.prepare_registration(decision_id)
        except (KeyError, ValueError) as e:
            self._send(f"<h1>Error</h1><p>{_esc(str(e))}</p>", 400)
            return

        _STATE["preparation"] = prep
        _STATE["decision_id"] = decision_id

        ds = svc.get_decision(decision_id)

        body_html = STEP_INTENT.format(
            desc=_STATE.get("description", ""),
            maxp=_STATE.get("maxp", "25"),
            maxr=_STATE.get("maxr", "35"),
        )
        body_html += _step_recommendation({
            "domain": ds.recommended_domain,
            "decision_id": ds.decision_id,
            "status": ds.status.value,
        })
        body_html += _step_checkout(ds.recommended_domain, {
            **prep, "decision_id": decision_id,
        })
        body_html += _api_trace_panel(ds.api_trace)

        self._send(body_html)

    def _handle_approve(self, body: dict):
        """Approve and register via DomainService."""
        decision_id = body.get("decision_id", [""])[0]
        svc = get_service()

        # Approve
        try:
            approval = svc.approve(decision_id)
        except (KeyError, ValueError) as e:
            self._send(f"<h1>Error</h1><p>{_esc(str(e))}</p>", 400)
            return

        # Register
        try:
            reg = svc.register(decision_id, approval["approval_token"])
        except (KeyError, ValueError, PermissionError) as e:
            self._send(f"<h1>Error</h1><p>{_esc(str(e))}</p>", 400)
            return

        # Configure DNS
        try:
            dns = svc.configure_dns(decision_id)
        except (KeyError, ValueError) as e:
            dns = {"error": str(e)}

        ds = svc.get_decision(decision_id)
        _STATE["registration"] = reg
        _STATE["dns"] = dns

        body_html = STEP_INTENT.format(
            desc=_STATE.get("description", ""),
            maxp=_STATE.get("maxp", "25"),
            maxr=_STATE.get("maxr", "35"),
        )
        body_html += _step_recommendation({
            "domain": ds.recommended_domain,
            "decision_id": ds.decision_id,
            "status": ds.status.value,
        })
        body_html += _step_checkout(ds.recommended_domain, {
            **(_STATE.get("preparation") or {}),
            "decision_id": decision_id,
            "status": "APPROVED",
        })
        body_html += _step_registered(ds.recommended_domain, {
            **reg, "decision_id": decision_id,
        })
        body_html += _step_dns(ds.recommended_domain, dns)
        if dns.get("dns_receipt_verified"):
            body_html += _step_verified(ds.recommended_domain, {
                "receipt_hash": dns.get("receipt_hash", ""),
            })
        body_html += _api_trace_panel(ds.api_trace)

        self._send(body_html)

    def _handle_reject(self, body: dict):
        """Reject the recommendation."""
        decision_id = body.get("decision_id", [""])[0]
        svc = get_service()
        svc.reject(decision_id)

        body_html = STEP_INTENT.format(
            desc=_STATE.get("description", ""),
            maxp=_STATE.get("maxp", "25"),
            maxr=_STATE.get("maxr", "35"),
        )
        body_html += '<div class="step"><span class="step-num">-</span><div class="step-title">REJECTED</div><div class="step-sub">Domain not approved for registration</div></div>'
        self._send(body_html)

    def _handle_configure_dns(self, body: dict):
        """Configure DNS via DomainService."""
        decision_id = body.get("decision_id", [""])[0]
        svc = get_service()

        try:
            dns = svc.configure_dns(decision_id)
        except (KeyError, ValueError) as e:
            self._send(f"<h1>Error</h1><p>{_esc(str(e))}</p>", 400)
            return

        ds = svc.get_decision(decision_id)
        _STATE["dns"] = dns

        body_html = STEP_INTENT.format(
            desc=_STATE.get("description", ""),
            maxp=_STATE.get("maxp", "25"),
            maxr=_STATE.get("maxr", "35"),
        )
        body_html += _step_recommendation({
            "domain": ds.recommended_domain,
            "decision_id": ds.decision_id,
            "status": ds.status.value,
        })
        body_html += _step_registered(ds.recommended_domain, {
            **(_STATE.get("registration") or {}),
            "decision_id": decision_id,
        })
        body_html += _step_dns(ds.recommended_domain, dns)
        if dns.get("dns_receipt_verified"):
            body_html += _step_verified(ds.recommended_domain, {
                "receipt_hash": dns.get("receipt_hash", ""),
            })
        body_html += _api_trace_panel(ds.api_trace)

        self._send(body_html)

    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == "__main__":
    print(f"DomainArena demo: http://127.0.0.1:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
