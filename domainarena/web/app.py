"""DomainArena demo UI — dependency-free (stdlib http.server) three-screen flow.

Screen 1: intent + audience + budget form
Screen 2: evidence table (feasible / rejected-with-reasons)
Screen 3: recommendation with explanation + approval gate

Run: python3 -m domainarena.web.app  → http://127.0.0.1:8777
"""
from __future__ import annotations
import asyncio
import html
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from domainarena.models import ConstraintSet  # noqa: E402
from domainarena.pipeline import recommend_live  # noqa: E402
from domainarena.providers.namecom import client_from_env  # noqa: E402

PORT = int(os.environ.get("DOMAINARENA_PORT", "8777"))

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>DomainArena</title>
<style>
 /*font-family:-apple-system,Segoe UI,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;background:#0d1117;color:#e6edf3*/
 h1{{{{color:#58a6ff}}}} .card{{{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;margin:16px 0*/
 input,select{{{{background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:8px;width:100%*/
 button{{{{background:#238636;color:#fff;border:0;border-radius:6px;padding:10px 24px;font-size:16px;cursor:pointer*/
 table{{{{width:100%;border-collapse:collapse}}}} td,th{{{{padding:6px 10px;border-bottom:1px solid #21262d;text-align:left*/
 .rej{{{{color:#f85149}}}} .ok{{{{color:#3fb950}}}} .muted{{{{color:#8b949e}}}} .big{{{{font-size:28px;color:#58a6ff*/
</style></head><body>
<h1>⚔️ DomainArena</h1>
<p class="muted">Evidence-based domain selection over name.com live inventory — not a name generator.</p>
{body}
</body></html>"""

FORM = """
<div class="card">
<form method="post" action="/run">
 <label>Product description<br><input name="description" value="Repairs malformed JSON for AI agents"></label><br><br>
 <label>Primary job<br><input name="primary_job" value="repair JSON"></label><br><br>
 <label>Audience
 <select name="audience">
  <option value="ai_agent">AI agents (machine-facing)</option>
  <option value="developer">Developers</option>
  <option value="business">Business</option>
  <option value="consumer">Consumers</option>
 </select></label><br><br>
 <label>Max first-year price ($)<input name="maxp" value="20" size="6" style="width:100px"></label>
 <label>Max renewal ($)<input name="maxr" value="30" size="6" style="width:100px"></label><br><br>
 <button type="submit">Run arena</button>
</form></div>"""


def _esc(s):
    return html.escape(str(s), quote=False)


async def _do_run(form) -> str:
    constraints = ConstraintSet(
        max_purchase_price=float(form.get("maxp", ["20"])[0] or 20),
        max_renewal_price=float(form.get("maxr", ["30"])[0] or 30))
    try:
        res = await recommend_live(
            description=form.get("description", [""])[0],
            primary_job=form.get("primary_job", [""])[0],
            audiences=[form.get("audience", ["ai_agent"])[0]],
            constraints=constraints,
            client=client_from_env())
    except Exception as e:
        return f'<div class="card"><span class="rej">name.com error: {_esc(e)}</span></div>' + FORM

    d = res.to_dict()
    rec = d["recommendation"]

    # AI inference cards: what does each model family see in this domain?
    inference_cards = ""
    try:
        from domainarena.arena.semantic_inversion import run_semantic_inversion
        inv_res = run_semantic_inversion(res.feasible, form.get("description", [""])[0])
        for r in inv_res:
            job = _esc(getattr(r, 'inferred_job', '')[:120] or '(no inference)')
            score = getattr(r, 'score', None)
            score_str = f"{score:.2f}" if score is not None else '?'
            inference_cards += (
                f'<div class="card"><b>{_esc(r.domain_name)}</b>'
                f' <span class="ok">semantic score: {score_str}</span>'
                f'<br>AI infers: {job}</div>')
    except Exception as e:
        inference_cards = f'<div class="card muted">inference unavailable: {_esc(e)}</div>'

    rows_feasible = "".join(
        f"<tr><td>{_esc(c.domain_name)}</td>"
        f"<td>${c.inventory.purchase_price}</td><td>${c.inventory.renewal_price}</td></tr>"
        for c in res.feasible)
    rows_rejected = "".join(
        f"<tr><td>{_esc(dom)}</td><td class='rej'>{_esc(', '.join(reasons))}</td></tr>"
        for dom, reasons in list(d["rejected"].items())[:10])
    return f"""
<div class="card">
 <div class="muted">intent {d['intent_hash'][:19]}… · {d['raw_candidates']} generated ·
 {d['in_inventory']} in name.com inventory · {len(d['feasible'])} feasible under budget</div>
 <h3>Recommendation</h3>
 <div class="big">{_esc(rec['domain']) if rec else '— none feasible under these constraints —'}</div>
 {('' if not rec else '<ul>' + ''.join(f'<li>{_esc(x)}</li>' for x in rec['explanation']) + '</ul>'
   + f"<p>Pareto-optimal: {'<span class=ok>yes</span>' if rec['on_pareto_front'] else 'no'} · score {_esc(rec['score'])}</p>")}
</div>
{inference_cards}
<div class="card"><h3>Feasible candidates (live inventory)</h3>
<table><tr><th>domain</th><th>first year</th><th>renewal</th></tr>{rows_feasible}</table></div>
<div class="card"><h3>Eliminated by hard constraints</h3>
<p class="muted">Budgets REMOVE candidates — they are never scored lower.</p>
<table><tr><th>domain</th><th>reasons</th></tr>{rows_rejected}</table></div>
<div class="card muted">Registration is approval-gated and disabled while no sandbox is available.</div>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body):
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path == "/health":
            return self._send("ok")
        self._send(PAGE.replace("{body}", FORM))

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(n).decode())
        try:
            body = asyncio.run(_do_run(form))
        except Exception as e:  # noqa: BLE001
            body = f'<div class="card rej">error: {_esc(e)}</div>' + FORM
        self._send(PAGE.replace('{body}', body))

    def log_message(self, *a):  # quiet
        pass


if __name__ == "__main__":
    print(f"DomainArena UI on http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
