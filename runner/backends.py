"""Provider-neutral clean-session runner backends (abuse.md item 3).

Each backend = one fresh isolated inference session per trial.
Records model/provider/version/runtime with every observation.
"""
import os, time, json, urllib.request, uuid

class CloudflareBackend:
    """Cloudflare Workers AI — @cf/openai/gpt-oss-120b (or any CF model id)."""
    name = "cloudflare-workers-ai"

    def __init__(self, account_id=None, token=None, model="@cf/meta/llama-3.2-3b-instruct"):
        self.account_id = account_id or os.environ.get("CF_ACCOUNT_ID", "954612afb5a97bb15dddcdc70176813d")
        self.token = token or os.environ.get("CF_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")
        if not self.account_id: self.account_id = os.environ.get("CF_ACCOUNT_ID", "")
        self.model = model

    def run(self, prompt: str, timeout=60):
        t0 = time.time()
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        body = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": 300}).encode()
        req = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            msg = d.get("result", {}).get("choices", [{}])[0].get("message", {})
            return {"ok": True, "raw": (msg.get("content") or "").strip(),
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

def get_backend(preferred="cloudflare"):
    order = [preferred] + [b for b in ("cloudflare", "opencode-go") if b != preferred]
    for name in order:
        if name == "cloudflare":
            b = CloudflareBackend()
        else:
            b = HermesBackend()
        # health probe
        probe = b.run("Reply with the single word OK.", timeout=30)
        if probe["ok"]:
            print(f"  backend [{name}] healthy ({probe['latency_ms']}ms)")
            return b, probe
        print(f"  backend [{name}] unhealthy: {probe.get('error') or probe['raw'][:60]}")
    raise RuntimeError("No healthy inference backend")
