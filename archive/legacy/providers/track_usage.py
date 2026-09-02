#!/usr/bin/env python3
"""Append a usage row to providers/usage.csv after each inference call.
Call from any backend wrapper:
    from track_usage import log_call
    log_call("groq", "openai/gpt-oss-120b", latency_ms=812, headers=r.headers)
"""
import csv, os, time

CSV = os.path.join(os.path.dirname(__file__), "usage.csv")
FIELDS = ["ts", "provider", "model", "latency_ms", "ok", "remaining_requests",
          "remaining_tokens", "limit_requests", "limit_tokens"]

def log_call(provider, model, latency_ms=None, ok=True, headers=None):
    row = {"ts": int(time.time()), "provider": provider, "model": model,
           "latency_ms": latency_ms, "ok": int(bool(ok)),
           "remaining_requests": "", "remaining_tokens": "",
           "limit_requests": "", "limit_tokens": ""}
    if headers is not None:
        g = lambda k: (headers.get(k) or headers.get(k.replace("-", "_")) or "")
        row.update({
            "remaining_requests": g("x-ratelimit-remaining-requests"),
            "remaining_tokens": g("x-ratelimit-remaining-tokens"),
            "limit_requests": g("x-ratelimit-limit-requests"),
            "limit_tokens": g("x-ratelimit-limit-tokens"),
        })
    new = not os.path.exists(CSV)
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new: w.writeheader()
        w.writerow(row)

if __name__ == "__main__":
    # quick self-test + show today's usage summary
    import collections
    if not os.path.exists(CSV):
        print("no usage yet"); raise SystemExit
    rows = list(csv.DictReader(open(CSV)))
    by = collections.Counter((r["provider"], r["model"]) for r in rows)
    for (p, m), n in sorted(by.items()):
        print(f"{n:5d}  {p:12s} {m}")
