"""Tests for score.py. Run: python -m pytest -q tests  (or python tests/test_score.py)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import score  # noqa: E402

A, B, C = [[1]], [[2]], [[3, 3]]
SOLUTIONS = {"t1": [A], "t2": [A, B], "t3": [C]}


def test_top2_partial_credit_and_missing_tasks():
    sub = {"t1": [{"attempt_1": B, "attempt_2": A}],
           "t2": [{"attempt_1": A, "attempt_2": A}, {"attempt_1": C, "attempt_2": C}]}
    got = score.score(SOLUTIONS, sub)
    assert got["top2"] == round(100 * (1 + 0.5 + 0) / 3, 4)
    assert got["top2_tasks_solved"] == 1
    assert "oracle" not in got


def test_oracle_uses_candidates_and_caps_at_100_distinct():
    sub = {}
    far = [[[9]]] * 50 + [[[i]] for i in range(10, 200)] + [C]  # C is distinct candidate 191
    cands = {"t1": [[B, A]], "t2": [[A], [B]], "t3": [far]}
    got = score.score(SOLUTIONS, sub, cands)
    assert got["top2"] == 0
    assert got["oracle"] == round(100 * 2 / 3, 4)


def test_mdlarc_candidates_format():
    raw = {"format": 1, "expected_candidates_per_test_output": 2, "pairs": [
        {"task_id": "t2", "pair_index": 1, "candidates": [{"grid": B, "count": 3}]},
        {"task_id": "t2", "pair_index": 0, "candidates": [{"grid": C, "count": 2}, {"grid": A, "count": 1}]},
    ]}
    assert score.normalise_candidates(raw) == {"t2": [[C, A], [B]]}


def test_unknown_tasks_warn():
    got = score.score(SOLUTIONS, {"zzz": [{"attempt_1": A, "attempt_2": A}]})
    assert "warning" in got and got["top2"] == 0


def _record(tmp_path, top2, oracle, launch=False):
    folder = tmp_path / "records" / "main" / "2026-01-01_test"
    run = folder / "arc1" / "seed0"
    run.mkdir(parents=True)
    (folder / "README.md").write_text("# test\n")
    (run / "submission.json").write_text(json.dumps(
        {"t1": [{"attempt_1": A, "attempt_2": A}], "t2": [{"attempt_1": A, "attempt_2": B}, {}]}))
    (run / "candidates.json").write_text(json.dumps({"t2": [[A], [B]], "t3": [[C]]}))
    meta = {"name": "t", "authors": ["x"], "tier": "main", "date": "2026-01-01", "params": 1,
            "code": {"url": "u", "commit": "c", "command": "x"},
            "results": {"arc1": {"runs": [{"seed": 0, "top2": top2, "oracle": oracle, "dir": "arc1/seed0"}],
                                 "top2_mean": top2, "compute": {"hardware": "1x CPU"}}, "arc2": None}}
    (folder / "record.json").write_text(json.dumps(meta))
    return folder


def test_verify_accepts_matching_record(tmp_path):
    folder = _record(tmp_path, top2=50.0, oracle=66.6667)
    assert score.verify(folder, {"arc1": SOLUTIONS}) == []


def test_verify_rejects_wrong_claim(tmp_path):
    folder = _record(tmp_path, top2=60.0, oracle=66.6667)
    problems = score.verify(folder, {"arc1": SOLUTIONS})
    assert any("top2 claimed 60.0" in p for p in problems)


if __name__ == "__main__":
    import tempfile
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            if "tmp_path" in fn.__code__.co_varnames[:fn.__code__.co_argcount]:
                with tempfile.TemporaryDirectory() as d:
                    fn(Path(d))
            else:
                fn()
            print("ok", name)
