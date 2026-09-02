#!/usr/bin/env python3
"""QLEX: build the Agent Query Lexicon.
Corpus A: elicit search queries from canonical models on standardised tasks.
Corpus B: sample Moltbook Observatory Archive via HF datasets-server API (no full download).
Output: results/experiments/qlex/lexicon.json
"""
import sys, os, json, re, time, datetime, hashlib, urllib.request
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

TASKS = {
    "domain_check": "Find out whether the domain name quietbrook-labs.com is available to register.",
    "price_lookup": "Find the current price of the cheapest managed Postgres database tier.",
    "code_fix": "My Python script throws ModuleNotFoundError for a package I installed. Find how to fix it.",
    "fact_verify": "Verify whether the Eiffel Tower is taller than the Golden Gate Bridge.",
    "file_convert": "Find a way to convert a HEIC image to PNG on a Linux server without GUI.",
    "email_validate": "Check whether the email address billing@example-corp.io can receive mail.",
}

ELICIT_PROMPT = """You are a research assistant with web search access.

Task: {task}

Write the exact search query you would type into a search engine first.
Respond with ONLY one line: QUERY: <your query>"""

MODELS = [
    ("cf", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
    ("cf", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
    ("cf", "@cf/openai/gpt-oss-20b"),
    ("or", "nvidia/nemotron-3-super-120b-a12b:free"),
]
ENDPOINTS = {
    "cf": ("https://api.cloudflare.com/client/v4/accounts/" + os.environ.get("CF_ACCOUNT_ID", "") + "/ai/run/", os.environ.get("CF_TOKEN")),
    "or": ("https://openrouter.ai/api/v1/chat/completions", os.environ.get("OPENROUTER_API_KEY")),
}


def call(kind, model, prompt, timeout=90, temperature=0):
    url, key = ENDPOINTS[kind]
    if kind == "cf":
        url = url + model
    body_obj = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 400, "temperature": temperature}
    if kind != "cf":
        body_obj["model"] = model
    req = urllib.request.Request(url, data=json.dumps(body_obj).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "User-Agent": "qlex/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
        res = d.get("result", {})
        msg = res["choices"][0]["message"] if "choices" in res else d["choices"][0]["message"]
        return (msg.get("content") or "").strip()
    except Exception:
        return ""


def harvest_queries(reps=3, temperature=0):
    out = []
    for tfam, task in TASKS.items():
        for kind, model in MODELS:
            for rep in range(reps):
                raw = call(kind, model, ELICIT_PROMPT.format(task=task), temperature=temperature)
                m = re.search(r'QUERY:\s*(.+)', raw)
                q = m.group(1).strip().strip('"') if m else ""
                out.append({"task_family": tfam, "model": model.split("/")[-1], "query": q})
                time.sleep(1)
    return [o for o in out if o["query"]]


STOP = set("a an and or the of to for in on with is are be by at from as that this it how do does can i my what".split())


def tokenize(q):
    return [w.lower().strip('.,?!"\'()') for w in q.split() if w.lower().strip('.,?!"\'()') not in STOP and len(w) > 1]


def freq_table(queries):
    from collections import Counter
    c = Counter()
    for o in queries:
        c.update(tokenize(o["query"]))
    return dict(c.most_common(60))


def moltbook_sample(limit=800):
    """Sample Moltbook posts via HF datasets-server (search endpoint, no auth needed)."""
    posts = []
    try:
        url = ("https://datasets-server.huggingface.co/rows?dataset=SimulaMet%2Fmoltbook-observatory-archive"
               "&config=posts&split=archive&offset=0&length=100")
        req = urllib.request.Request(url, headers={"User-Agent": "qlex/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        rows = d.get("rows", [])
        for row in rows[:100]:
            rj = row.get("row", {})
            txt = rj.get("content") or rj.get("body") or rj.get("text") or ""
            if txt:
                posts.append(txt[:500])
    except Exception as e:
        print(f"  moltbook sample unavailable ({str(e)[:60]}) - proceeding elicited-only")
    return posts


if __name__ == "__main__":
    TEMP = float(os.environ.get("QLEX_TEMP", "0"))
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments/qlex"
    os.makedirs(outdir, exist_ok=True)

    spec = {"experiment": "QLEX", "protocol_version": 2, "seed_tasks": list(TASKS),
            "models": [m[1] for m in MODELS], "reps_per_cell": 3, "temperature": "env QLEX_TEMP"}
    spec["manifest_hash"] = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    json.dump({**spec, "ts": stamp}, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)

    print("harvesting elicited queries…")
    queries = harvest_queries(temperature=TEMP)
    print(f"  got {len(queries)} queries")

    print("sampling observatory corpus…")
    obs_posts = moltbook_sample()

    lex = {
        "generated": stamp,
        "manifest_hash": spec["manifest_hash"],
        "elicited_queries": queries,
        "overall_freq_top60": freq_table(queries),
        "per_task_freq": {tf: freq_table([q for q in queries if q["task_family"] == tf]) for tf in TASKS},
        "observatory_sample_n": len(obs_posts),
        "observatory_terms_of_interest": {t: sum(t in p.lower() for p in obs_posts)
                                           for t in ["api", "tool", "free", "verify", "verified",
                                                     "check", "convert", "lookup", "agent-friendly",
                                                     "mcp", "llms.txt", "x402"]},
    }
    json.dump(lex, open(f"{outdir}/lexicon_{stamp}.json", "w"), indent=1)
    print(f"saved {outdir}/lexicon_{stamp}.json")
