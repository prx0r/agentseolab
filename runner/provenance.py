"""Runtime provenance — every trial records its actual execution identity."""
import hashlib, json, os

RUNNER_VERSION = "asl-runner/0.2.0"

def phash(s): return "sha256:" + hashlib.sha256(s.encode()).hexdigest()[:16]

def trial_provenance(backend, prompt, response_raw, ordering, extra=None):
    return {
        "provider": backend.name,
        "model_id": getattr(backend, "model", None) or f"{backend.name}-profile",
        "model_revision": getattr(backend, "revision", None),
        "temperature": 0,
        "max_tokens": getattr(backend, "max_tokens", 300),
        "api_surface": "openai-chat-completions",
        "runner_version": RUNNER_VERSION,
        "prompt_hash": phash(prompt),
        "response_hash": phash(response_raw or ""),
        "ordering": ordering,
        **(extra or {}),
    }
