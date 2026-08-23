"""Provider-neutral clean-session runner backends (abuse.md item 3).

Each backend = one fresh isolated inference session per trial.
Records model/provider/version/runtime with every observation.
"""
import os, time, json, urllib.request, uuid
import os as _os
from pathlib import Path as _Path
_envf = _Path(__file__).parent / '.env'
if _envf.exists():
    for _line in _envf.read_text().splitlines():
        if '=' in _line and not _line.startswith('#'):
            _k, _v = _line.split('=', 1)
            _os.environ.setdefault(_k.strip(), _v.strip())



FREE_CF_MODELS = [
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "@cf/qwen/qwen3-30b-a3b-fp8",
    "@cf/deepseek-ai/deepseek-v4-flash-0731",
    "@cf/openai/gpt-oss-20b",
]

class CloudflareBackend:
    """Cloudflare Workers AI — rotate across free model families."""
    name = "cloudflare-workers-ai"

    def __init__(self, account_id=None, token=None, model="@cf/meta/llama-3.3-70b-instruct-fp8-fast"):
        self.account_id = account_id or os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
        self.token = token or os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")
        if not self.account_id: self.account_id = os.environ.get("CF_ACCOUNT_ID", "")
        self.model = model

    def run(self, prompt: str, timeout=60):
        t0 = time.time()
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        body = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": 1200}).encode()
        req = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            res = d.get("result", {})
            # Chat models: result.choices[].message.content; instruct models: result.response
            msg = res.get("choices", [{}])[0].get("message", {}) if "choices" in res else {}
            text = (msg.get("content") or res.get("response") or "").strip()
            return {"ok": True, "raw": text,
                    "reasoning_present": bool(msg.get("reasoning")),
                    "session_id": "cf_" + uuid.uuid4().hex[:10],
                    "latency_ms": int((time.time()-t0)*1000)}
        except Exception as e:
            return {"ok": False, "raw": "", "error": str(e)[:120],
                    "session_id": "cf_" + uuid.uuid4().hex[:10],
                    "latency_ms": int((time.time()-t0)*1000)}




class HermesBackend:
    """Hermes CLI profile (opencode-go). Currently quota-blocked; auto-fallback target."""
    name = "opencode-go"
    def __init__(self, profile="builder"):
        self.profile = profile
    def run(self, prompt: str, timeout=90):
        import subprocess
        t0 = time.time()
        try:
            out = subprocess.run(["hermes", "-p", self.profile, "-z", prompt],
                                 capture_output=True, text=True, timeout=timeout)
            return {"ok": out.returncode == 0 and bool(out.stdout.strip()),
                    "raw": (out.stdout or "").strip()[-500:], "exit_code": out.returncode,
                    "session_id": "hm_" + uuid.uuid4().hex[:10],
                    "latency_ms": int((time.time()-t0)*1000)}
        except subprocess.TimeoutExpired:
            return {"ok": False, "raw": "", "error": "timeout",
                    "session_id": "hm_" + uuid.uuid4().hex[:10],
                    "latency_ms": int((time.time()-t0)*1000)}

from opencode_direct import OpenCodeDirect

def get_backend(preferred="opencode"):
    order = [preferred] + [b for b in ("opencode", "cloudflare") if b != preferred]
    for name in order:
        if name == "cloudflare":
            b = CloudflareBackend()
        elif name == "opencode":
            b = OpenCodeDirect()
        else:
            b = HermesBackend()
        # health probe
        probe = b.run("Reply with the single word OK.", timeout=30)
        if probe["ok"]:
            print(f"  backend [{name}] healthy ({probe['latency_ms']}ms)")
            return b, probe
        print(f"  backend [{name}] unhealthy: {probe.get('error') or probe['raw'][:60]}")
    raise RuntimeError("No healthy inference backend")
