from domainarena.arena.ablation import run_ablation
from domainarena.arena.discovery import DiscoveryRun, mock_backend
from domainarena.arena.execution import SandboxService
from domainarena.receipts import build_receipt, receipt_hash, verify_receipt


class TestDiscovery:
    def test_stratified_stats_and_mock(self):
        cands = ["jsonrepair.dev", "velora.com", "fixit.io"]
        run = DiscoveryRun("repair malformed JSON", cands)
        backend = mock_backend(lambda top, prompt: "jsonrepair.dev"
                               if "jsonrepair" in prompt else None)
        trials = run.run_trials(backend, n_per_family=12)
        assert len(trials) == 12
        s = run.stats()
        assert s["n_decided"] == 12 and s["n_errors"] == 0
        # jsonrepair always picked regardless of slot -> pos0/off rates differ
        pc = s["per_candidate"]["jsonrepair.dev"]
        assert pc["p_pick_given_pos0"] == 1.0 or pc["p_pick_given_offpos0"] == 1.0

    def test_slots_are_permutations(self):
        run = DiscoveryRun("task", ["a.com", "b.com", "c.dev", "d.io"])
        backend = mock_backend(lambda top, prompt: None)
        trials = run.run_trials(backend, n_per_family=6)
        assert all(sorted(t.slots.values()) == [0, 1, 2, 3] for t in trials)


class TestAblation:
    def test_five_methods_ranked_and_scored(self):
        services = {
            "jsonrepair.dev": SandboxService("jsonrepair.dev"),
            "velora.com": SandboxService("velora.com", works=False),
        }
        res = run_ablation("repair malformed JSON", list(services), services,
                           "repairs malformed JSON")
        methods = {r.method for r in res}
        assert methods == {"baseline_llm", "heuristic", "semantic_only",
                           "pairwise_arena", "execution_grounded"}
        eg = next(r for r in res if r.method == "execution_grounded")
        assert eg.ranking[0] == "jsonrepair.dev"
        assert eg.useful_selection == 1.0


class TestReceipts:
    def test_receipt_hash_roundtrip(self):
        r = build_receipt(intent_hash="sha256:x", description="d",
                          primary_job="j", audience="ai_agent",
                          constraints_dict={}, feasible_domains=["a.dev"],
                          rejected={}, recommendation=None,
                          source="demo-fixture", policy_version="v1")
        h = receipt_hash(r)
        import json, tempfile, pathlib
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({**r, "manifest_hash": h}, f)
            p = pathlib.Path(f.name)
        assert verify_receipt(p)

    def test_tamper_detection(self):
        r = build_receipt(intent_hash="sha256:x", description="d",
                          primary_job="j", audience="ai_agent",
                          constraints_dict={}, feasible_domains=["a.dev"],
                          rejected={}, recommendation=None,
                          source="s", policy_version="v")
        import json, tempfile, pathlib
        h = receipt_hash(r)
        r["feasible_domains"] = ["evil.dev"]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({**r, "manifest_hash": h}, f)
            p = pathlib.Path(f.name)
        assert not verify_receipt(p)
