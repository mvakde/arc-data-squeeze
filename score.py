#!/usr/bin/env python3
"""Score ARC Data Squeeze predictions, or verify a record folder.

    python score.py --benchmark arc1 submission.json
    python score.py --benchmark arc1 submission.json --candidates candidates.json.gz
    python score.py --verify records/open/2026-11-10_looped-mdlarc-d384x6-rearc

Top-2 (the ranked score) is the official ARC Prize metric. Each test input gets two attempts. A task scores the
fraction of its test inputs where attempt_1 or attempt_2 equals the answer exactly. The total is the mean over
the evaluated tasks, as a percentage. Missing tasks score 0.

Oracle (always reported, never ranked): the answer is among the first 100 distinct candidates for that test
input. Aggregated the same way. The gap between oracle and top-2 shows whether a method fails to find the
answer or fails to pick it.

Accepted files (plain JSON or .json.gz):
  submission   ARC Prize format: {task_id: [{"attempt_1": grid, "attempt_2": grid}, ... one per test input]}
  candidates   {task_id: [[grid, grid, ...], ... one list per test input]}, best first; or
               the looped mdlARC baseline's candidates.json.gz ({"format": 1, "pairs": [...]})

Standard library only. Needs the solutions from `python prepare_data.py`.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BENCHMARKS = {"arc1": "ARC-AGI-1", "arc2": "ARC-AGI-2"}
TRACKS = ("main", "open")  # records, and interesting results outside the rules (RULES.md, section 9)
MAX_CANDIDATES = 100
TOLERANCE = 0.01  # percentage points allowed between a claimed and a re-scored number


def load(path: Path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as handle:
        return json.load(handle)


def default_solutions(benchmark: str) -> Path:
    path = ROOT / "data" / "main" / benchmark / "solutions.json"
    if path.exists():
        return path
    sys.exit(f"No solutions for {benchmark}. Run `python prepare_data.py` first, or pass --solutions.")


def normalise_candidates(raw) -> dict:
    """Return {task_id: [[grid, ...] per test input]}."""
    if isinstance(raw, dict) and raw.get("format") == 1 and "pairs" in raw:
        out: dict = {}
        for pair in raw["pairs"]:
            slots = out.setdefault(pair["task_id"], [])
            while len(slots) <= pair["pair_index"]:
                slots.append([])
            slots[pair["pair_index"]] = [c["grid"] for c in pair["candidates"]]
        return out
    if isinstance(raw, dict):
        return raw
    raise ValueError("unrecognised candidates file")


def distinct(grids, limit=MAX_CANDIDATES):
    seen, out = set(), []
    for grid in grids:
        key = json.dumps(grid)
        if key not in seen:
            seen.add(key)
            out.append(grid)
            if len(out) == limit:
                break
    return out


def score(solutions: dict, submission: dict, candidates: dict | None = None) -> dict:
    top2_total = oracle_total = 0.0
    solved, found = [], []
    for task_id, truths in solutions.items():
        attempts = submission.get(task_id) or []
        options = (candidates or {}).get(task_id) or []
        hits = oracle_hits = 0
        for i, truth in enumerate(truths):
            entry = attempts[i] if i < len(attempts) and isinstance(attempts[i], dict) else {}
            if entry.get("attempt_1") == truth or entry.get("attempt_2") == truth:
                hits += 1
            if i < len(options) and truth in distinct(options[i]):
                oracle_hits += 1
        top2_total += hits / len(truths)
        oracle_total += oracle_hits / len(truths)
        if hits == len(truths):
            solved.append(task_id)
        if oracle_hits == len(truths):
            found.append(task_id)
    n = len(solutions)
    result = {"tasks": n, "test_inputs": sum(len(t) for t in solutions.values()),
              "top2": round(100 * top2_total / n, 4), "top2_tasks_solved": len(solved)}
    if candidates is not None:
        result.update({"oracle": round(100 * oracle_total / n, 4), "oracle_tasks_solved": len(found)})
    unknown = sorted(set(submission) - set(solutions))
    if unknown:
        result["warning"] = f"{len(unknown)} task id(s) in the submission are not in this benchmark"
    return result


# ---------------------------------------------------------------- record verification

REQUIRED = ("name", "authors", "track", "date", "params", "code", "results")


def verify(folder: Path, solutions_override: dict | None = None) -> list[str]:
    """Check a record folder. Returns a list of problems (empty = verified)."""
    folder = Path(folder)
    problems: list[str] = []
    meta_path = folder / "record.json"
    if not (folder / "README.md").exists():
        problems.append("README.md is missing")
    if not meta_path.exists():
        return problems + ["record.json is missing"]
    meta = load(meta_path)
    for key in REQUIRED:
        if key not in meta:
            problems.append(f"record.json: '{key}' is missing")
    if meta.get("track") not in TRACKS:
        problems.append(f"record.json: track must be one of {', '.join(TRACKS)}")
    if folder.parent.name != meta.get("track"):
        problems.append(f"folder is under records/{folder.parent.name}/ but track is '{meta.get('track')}'")
    if meta.get("track") == "main" and meta.get("declared_components"):
        problems.append("record.json: a record cannot declare components beyond the rules; put it under records/open/")
    code = meta.get("code") or {}
    for key in ("url", "commit", "command"):
        if not code.get(key):
            problems.append(f"record.json: code.{key} is missing")

    results = meta.get("results") or {}
    if not any(results.get(b) for b in BENCHMARKS):
        problems.append("record.json: results need at least one benchmark (both is the norm)")
    for benchmark, block in results.items():
        if benchmark not in BENCHMARKS:
            problems.append(f"results: unknown benchmark '{benchmark}'")
            continue
        if not block:
            continue
        runs = block.get("runs") or []
        if not runs:
            problems.append(f"{benchmark}: no runs listed")
            continue
        solutions = (solutions_override or {}).get(benchmark) or load(default_solutions(benchmark))
        for run in runs:
            label = f"{benchmark} seed {run.get('seed')}"
            if run.get("dir") is None:
                if not meta.get("launch_entry"):
                    problems.append(f"{label}: predictions are required ('dir')")
                continue
            run_dir = folder / run["dir"]
            sub_path = run_dir / "submission.json"
            if not sub_path.exists():
                problems.append(f"{label}: {sub_path.relative_to(folder)} is missing")
                continue
            cand_path = next((p for p in (run_dir / "candidates.json.gz", run_dir / "candidates.json")
                              if p.exists()), None)
            got = score(solutions, load(sub_path), normalise_candidates(load(cand_path)) if cand_path else None)
            for metric in ("top2", "oracle"):
                claimed = run.get(metric)
                if metric == "oracle" and cand_path is None:
                    if claimed is not None:
                        problems.append(f"{label}: oracle claimed but no candidates file")
                    continue
                if claimed is None or abs(got[metric] - claimed) > TOLERANCE:
                    problems.append(f"{label}: {metric} claimed {claimed}, re-scored {got[metric]}")
        claimed_mean = block.get("top2_mean")
        actual_mean = sum(r["top2"] for r in runs if r.get("top2") is not None) / len(runs)
        if claimed_mean is not None and abs(claimed_mean - actual_mean) > TOLERANCE:
            problems.append(f"{benchmark}: top2_mean {claimed_mean} is not the mean of the runs ({actual_mean:.4f})")
        if not (block.get("compute") or {}).get("hardware"):
            problems.append(f"{benchmark}: compute.hardware is missing")
    return problems


# ---------------------------------------------------------------- CLI

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("submission", nargs="?", type=Path)
    ap.add_argument("--benchmark", choices=BENCHMARKS)
    ap.add_argument("--candidates", type=Path)
    ap.add_argument("--solutions", type=Path, help="default: data/main/<benchmark>/solutions.json")
    ap.add_argument("--verify", nargs="+", type=Path, metavar="RECORD_DIR")
    ap.add_argument("--json", action="store_true", help="print machine-readable output")
    args = ap.parse_args()

    if args.verify:
        failed = 0
        for folder in args.verify:
            problems = verify(folder)
            failed += bool(problems)
            print(f"{'FAIL' if problems else 'ok  '} {folder}")
            for problem in problems:
                print(f"     - {problem}")
        return 1 if failed else 0

    if not (args.submission and args.benchmark):
        ap.error("give a submission file and --benchmark, or --verify RECORD_DIR")
    solutions = load(args.solutions or default_solutions(args.benchmark))
    candidates = normalise_candidates(load(args.candidates)) if args.candidates else None
    result = score(solutions, load(args.submission), candidates)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    name = BENCHMARKS[args.benchmark]
    print(f"{name}: {result['tasks']} tasks, {result['test_inputs']} test inputs")
    print(f"  top-2   {result['top2']:7.3f}%   ({result['top2_tasks_solved']} tasks fully solved)")
    if "oracle" in result:
        print(f"  oracle  {result['oracle']:7.3f}%   ({result['oracle_tasks_solved']} tasks fully solved, "
              f"<= {MAX_CANDIDATES} distinct candidates per test input)")
    if "warning" in result:
        print(f"  warning: {result['warning']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
