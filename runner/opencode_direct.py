"""Direct OpenCode Zen client — ox-alpha-free, no hermes CLI overhead."""
import os, json, time, urllib.request, uuid

class OpenCodeDirect:
    name = "opencode-go"
    model = "ox-alpha-free"

    def __init__(self, key=None, base="https://opencode.ai/zen/go/v1"):
        self.key = key or os.environ.get("OPENCODE_GO_API_KEY") or \
            (open("/root/agentseolab/runner/.env").read()
             .split("OPENCODE_GO_API_KEY=")[1].split("\n")[0]
             if os.path.exists("/root/agentseolab/runner/.env") else "")
        self.base = base

    def run(self, prompt, timeout=60):
        t0 = time.time()
        body = json.dumps({"model": self.model,
                           "messages": [{"role": "user", "content": prompt}],
                           "max_tokens": 300}).encode()
        req = urllib.request.Request(f"{self.base}/chat/completions", data=body,
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                     "User-Agent": "AgentSEOLab/0.2 (research runner)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            content = d["choices"][0]["message"].get("content") or ""
            return {"ok": bool(content.strip()), "raw": content.strip(),
                    "session_id": "zen_" + uuid.uuid4().hex[:10],
                    "latency_ms": int((time.time()-t0)*1000)}
        except Exception as e:
            return {"ok": False, "raw": "", "error": str(e)[:120],
                    "session_id": "zen_" + uuid.uuid4().hex[:10],
                    "latency_ms": int((time.time()-t0)*1000)}
