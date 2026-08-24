"""CP5 — Execution-grounded selection environment with hidden verifier.

The scientific moat. Agents receive a realistic task plus N equivalent services
differing only in hostname (identical descriptions per the TLD-fix rule). The
selected service actually executes against a deterministic sandbox; an injective,
deterministic verifier confirms the OUTCOME, never the agent's claims.

Funnel stages are recorded separately and never collapsed:
SELECTED → INVOKED → VALID_PARAMS → TASK_VERIFIED
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field


@dataclass
class SandboxService:
    """Deterministic fake capability bound to exactly one hostname."""
    domain: str
    works: bool = True

    def invoke(self, payload: str) -> dict:
        if not self.works:
            return {"ok": False, "error": "service error"}
        return {"ok": True, "result": {"echo": payload}}


@dataclass
class SelectionTrial:
    task_prompt: str                      # frozen; identical across candidates
    candidates: list[str]                 # hostnames, identical metadata otherwise
    description: str                      # SAME text for every candidate
    family: str                           # evaluator family provenance
    window_id: str = "w0"                 # serving-window replicate id (H-SERVE01)
    selected: str | None = None           # hostname chosen (None = abstention/error)
    invoked: bool = False
    valid_params: bool = False
    task_verified: bool = False
    raw_response: str = ""
    notes: list[str] = field(default_factory=list)


def _parse_selection(raw: str, candidates: list[str]) -> str | None:
    """Extract chosen hostname from a response. Injective: at most one candidate matches."""
    lowered = raw.lower()
    hits = [c for c in candidates if c.lower() in lowered]
    return hits[0] if len(hits) == 1 else None


VERIFIER_PROMPT = """Task: {task}

Available services (all equivalent):
{services}

Choose ONE service by hostname and reply with JSON:
{{"selected": "<hostname>", "payload": "<input string for the service>"}}
Reply {{"selected": null}} if none can perform the task.
"""


def run_trial(task_prompt: str, services: dict[str, SandboxService],
              description: str, family: str, backend_run,
              window_id: str = "w0") -> SelectionTrial:
    """One execution-grounded trial.

    `backend_run(prompt) -> {"ok": bool, "raw": str}` is the fresh-session
    inference callable for one model family.
    """
    cand_names = sorted(services)
    service_lines = "\n".join(f"- https://{c} — {description}" for c in cand_names)
    prompt = VERIFIER_PROMPT.format(task=task_prompt, services=service_lines)

    trial = SelectionTrial(task_prompt=task_prompt, candidates=cand_names,
                           description=description, family=family, window_id=window_id)
    resp = backend_run(prompt)
    trial.raw_response = resp.get("raw", "")
    if not resp.get("ok"):
        # failure ≠ change: errors are never counted as selections
        trial.notes.append(f"backend_error: {resp.get('error', 'unknown')[:120]}")
        return trial

    sel = _parse_selection(trial.raw_response, cand_names)
    if sel is None:
        m = re.search(r'"selected"\s*:\s*"([^"]+)"', trial.raw_response)
        sel = m.group(1) if m and m.group(1).lower() in [c.lower() for c in cand_names] else None
    if sel is None:
        return trial  # abstention or unparseable — data, not success
    trial.selected = sel

    try:
        payload_match = re.search(r'"payload"\s*:\s*"([^"]*)"', trial.raw_response)
        payload = payload_match.group(1) if payload_match else ""
        result = services[sel].invoke(payload)
        trial.invoked = True
        trial.valid_params = isinstance(payload, str) and len(payload) > 0
        # Hidden deterministic verification of the OUTCOME:
        trial.task_verified = bool(result.get("ok")) and trial.valid_params
        if not trial.task_verified:
            trial.notes.append(f"verifier_reject: {json.dumps(result)[:200]}")
    except Exception as e:  # noqa: BLE001
        trial.notes.append(f"invoke_error: {e}"[:200])
    return trial


def funnel(trials: list[SelectionTrial]) -> dict[str, float]:
    decided = [t for t in trials if t.selected is not None]
    n = len(trials) or 1
    d = len(decided) or 1
    return {
        "n_trials": len(trials),
        "selected": sum(1 for t in trials if t.selected) / n,
        "invoked": sum(1 for t in trials if t.invoked) / n,
        "valid_params": sum(1 for t in trials if t.valid_params) / n,
        "task_verified": sum(1 for t in trials if t.task_verified) / n,
        "conditional_invoked_given_selected":
            sum(1 for t in decided if t.invoked) / d,
        "conditional_verified_given_selected":
            sum(1 for t in decided if t.task_verified) / d,
    }


def useful_selection(trials: list[SelectionTrial]) -> float:
    """UsefulSelection(d) = P(select ∧ verified), pooled — report per-candidate elsewhere."""
    if not trials:
        return float("nan")
    return sum(1 for t in trials if t.task_verified) / len(trials)
