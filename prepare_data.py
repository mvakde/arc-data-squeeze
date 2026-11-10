#!/usr/bin/env python3
"""Build the ARC Data Squeeze training sets and check them against data/MANIFEST.json.

    python prepare_data.py                      # Main tier, ARC-AGI-1 and ARC-AGI-2
    python prepare_data.py --tier arc-only      # ARC-only tier
    python prepare_data.py --tier rearc         # +ReARC tier (downloads ~150 MB, writes ~1.4 GB)
    python prepare_data.py --tier all

Writes data/<tier>/<benchmark>/:
    challenges.json        every task you may train on, in the ARC Prize format. The evaluated
                           benchmark's tasks keep their demo pairs and test inputs; their test
                           outputs are removed. Every other task has all its pairs under "train".
    solutions.json         the withheld test outputs, for scoring only. Never train on them.
    rearc_challenges.json  +ReARC tier only: the 400 ARC-AGI-1 training tasks with up to 1,000
                           ReARC pairs each appended. These tasks are not repeated in challenges.json.

Standard library only. Upstream sources are pinned to commits. The files hold exactly the tasks and pairs of
the looped mdlARC baseline's `build_datasets.py --style pretrain` builds, so you can drop them into that code.
(That script orders the other benchmark's tasks by directory listing, which varies between machines; this one
always puts training before evaluation, so the SHA-256 checks hold everywhere.)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
import sys
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "data" / "MANIFEST.json"

SOURCES = {
    "arc1": ("https://github.com/fchollet/ARC-AGI/archive/{commit}.zip",
             "399030444e0ab0cc8b4e199870fb20b863846f34", "ARC-AGI-{commit}/data/"),
    "arc2": ("https://github.com/arcprize/ARC-AGI-2/archive/{commit}.zip",
             "f3283f727488ad98fe575ea6a5ac981e4a188e49", "ARC-AGI-2-{commit}/data/"),
    "conceptarc": ("https://github.com/victorvikram/ConceptARC/archive/{commit}.zip",
                   "0e67da6af879e4bad3d7cd3c196e8d551b445725", "ConceptARC-{commit}/corpus/"),
    "rearc": ("https://raw.githubusercontent.com/michaelhodel/re-arc/{commit}/re_arc.zip",
              "e5b7f1d06362a76f9d3b8c25154ff1fafca897ce", "re_arc/tasks/"),
}
TIERS = {  # tier: (ConceptARC, ReARC pairs per ARC-AGI-1 training task)
    "rearc": (True, 1000),
    "main": (True, None),
    "arc-only": (False, None),
}
BENCHMARKS = ("arc1", "arc2")
# ReARC pairs of this task that contradict the original task; the baseline drops them.
REARC_EXCLUDED = {"e26a3af2": frozenset({
    2, 12, 18, 26, 28, 32, 55, 60, 62, 77, 88, 106, 109, 112, 113, 116, 122, 141, 147, 151, 153, 154, 155,
    156, 158, 169, 172, 173, 180, 183, 201, 207, 211, 220, 227, 228, 236, 246, 255, 280, 286, 302, 311, 318,
    325, 329, 335, 353, 356, 361, 376, 378, 381, 393, 400, 421, 431, 444, 445, 451, 453, 473, 475, 491, 493,
    495, 508, 509, 512, 514, 516, 528, 539, 543, 560, 564, 568, 572, 591, 595, 600, 605, 607, 611, 612, 623,
    626, 627, 636, 647, 649, 651, 654, 661, 679, 688, 697, 699, 701, 705, 718, 726, 728, 753, 757, 759, 763,
    785, 796, 799, 800, 807, 829, 830, 834, 839, 847, 849, 857, 865, 889, 890, 896, 901, 915, 966, 970, 974,
    987})}


# ---------------------------------------------------------------- download

def fetch(name: str, cache: Path) -> zipfile.ZipFile:
    url, commit, _ = SOURCES[name]
    path = cache / f"{name}-{commit}.zip"
    if not path.exists():
        print(f"downloading {name} @ {commit[:7]}", flush=True)
        cache.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url.format(commit=commit)) as resp:
            blob = resp.read()
        tmp = path.with_suffix(".part")
        tmp.write_bytes(blob)
        tmp.replace(path)
    return zipfile.ZipFile(path)


def json_members(zf: zipfile.ZipFile, prefix: str):
    """(relative path parts, parsed JSON) for every .json under prefix, in pathlib sort order."""
    found = []
    for member in zf.namelist():
        if member.startswith(prefix) and member.endswith(".json"):
            found.append((PurePosixPath(member[len(prefix):]).parts, member))
    found.sort()
    return [(parts, json.loads(zf.read(member))) for parts, member in found]


def clean(task: dict) -> dict:
    return {"train": task["train"], "test": task["test"]}


def load_arc(name: str, cache: Path) -> dict:
    """{'training'|'evaluation': {task_id: {'train', 'test'}}} with test outputs present."""
    _, commit, prefix = SOURCES[name]
    out = {"training": {}, "evaluation": {}}
    for parts, task in json_members(fetch(name, cache), prefix.format(commit=commit)):
        if len(parts) == 2 and parts[0] in out:
            out[parts[0]][parts[1][:-5]] = clean(task)
    return out


def load_conceptarc(cache: Path) -> dict:
    _, commit, prefix = SOURCES["conceptarc"]
    return {parts[-1][:-5]: clean(task)
            for parts, task in json_members(fetch("conceptarc", cache), prefix.format(commit=commit))}


def load_rearc(cache: Path) -> dict:
    _, commit, prefix = SOURCES["rearc"]
    out = {}
    for parts, pairs in json_members(fetch("rearc", cache), prefix.format(commit=commit)):
        if len(parts) == 1:
            task_id = parts[0][:-5]
            skip = REARC_EXCLUDED.get(task_id, frozenset())
            out[task_id] = [p for i, p in enumerate(pairs) if i not in skip]
    return out


# ---------------------------------------------------------------- build

def flatten(tasks: dict) -> dict:
    """Every pair becomes a training pair: test pairs are appended to train."""
    return {tid: {"train": t["train"] + t.get("test", [])} for tid, t in tasks.items()}


def build(benchmark: str, tier: str, arc: dict, concept: dict, rearc: dict | None) -> dict:
    """Returns {filename: object} for one benchmark in one tier."""
    other = "arc2" if benchmark == "arc1" else "arc1"
    shared = (set(arc["arc1"]["training"]) | set(arc["arc1"]["evaluation"])) & \
             (set(arc["arc2"]["training"]) | set(arc["arc2"]["evaluation"]))
    # The other benchmark's tasks whose IDs do not appear in this one (training first, then evaluation).
    other_only = {tid: t for split in ("training", "evaluation")
                  for tid, t in arc[other][split].items() if tid not in shared}
    evaluated = arc[benchmark]["evaluation"]

    with_concept, rearc_pairs = TIERS[tier]
    challenges = dict(flatten(arc[benchmark]["training"]))
    if with_concept:
        challenges.update(flatten(concept))
    challenges.update(flatten(other_only))
    challenges.update({tid: {"train": t["train"], "test": [{"input": p["input"]} for p in t["test"]]}
                       for tid, t in evaluated.items()})
    outputs = {"solutions.json": {tid: [p["output"] for p in t["test"]] for tid, t in evaluated.items()}}

    if rearc_pairs is not None:
        rng = random.Random(0)
        rearc_tasks = {}
        for tid, task in sorted(flatten(arc["arc1"]["training"]).items()):
            if tid in evaluated:
                continue
            pool = rearc.get(tid, [])
            picked = rng.sample(pool, min(rearc_pairs, len(pool)))
            rearc_tasks[tid] = {"train": task["train"] + picked}
            challenges.pop(tid, None)
        outputs["rearc_challenges.json"] = rearc_tasks

    outputs["challenges.json"] = challenges
    return outputs


# ---------------------------------------------------------------- checks

def stats(name: str, obj: dict) -> dict:
    if name == "solutions.json":
        return {"tasks": len(obj), "withheld_outputs": sum(len(v) for v in obj.values())}
    return {"tasks": len(obj),
            "pairs": sum(len(t["train"]) for t in obj.values()),
            "test_inputs": sum(len(t.get("test", [])) for t in obj.values())}


def check_leak(challenges: dict, solutions: dict) -> None:
    for tid, outs in solutions.items():
        task = challenges[tid]
        assert all("output" not in p for p in task["test"]), f"{tid}: test output present"
        assert len(task["test"]) == len(outs), f"{tid}: test count mismatch"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", choices=[*TIERS, "all"], default="main")
    ap.add_argument("--benchmark", choices=[*BENCHMARKS, "both"], default="both")
    ap.add_argument("--out", type=Path, default=ROOT / "data", help="output root (default: data/)")
    ap.add_argument("--cache", type=Path, default=ROOT / "data" / "_downloads")
    ap.add_argument("--write-manifest", action="store_true", help="maintainers: record hashes instead of checking")
    args = ap.parse_args()

    tiers = list(TIERS) if args.tier == "all" else [args.tier]
    benchmarks = list(BENCHMARKS) if args.benchmark == "both" else [args.benchmark]
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"files": {}}

    arc = {name: load_arc(name, args.cache) for name in BENCHMARKS}
    concept = load_conceptarc(args.cache)
    rearc = load_rearc(args.cache) if "rearc" in tiers else None

    failures = 0
    for tier in tiers:
        for benchmark in benchmarks:
            outputs = build(benchmark, tier, arc, concept, rearc)
            check_leak(outputs["challenges.json"], outputs["solutions.json"])
            folder = args.out / tier / benchmark
            folder.mkdir(parents=True, exist_ok=True)
            for name, obj in sorted(outputs.items()):
                blob = json.dumps(obj).encode()
                (folder / name).write_bytes(blob)
                key = f"{tier}/{benchmark}/{name}"
                got = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob), **stats(name, obj)}
                if args.write_manifest:
                    manifest["files"][key] = got
                    status = "recorded"
                elif manifest["files"].get(key) == got:
                    status = "ok"
                else:
                    status = "MISMATCH"
                    failures += 1
                counts = ", ".join(f"{k} {v:,}" for k, v in got.items() if k not in ("sha256", "bytes"))
                print(f"{status:8} {key:38} {counts}")

    if args.write_manifest:
        manifest["sources"] = {k: {"url": u.format(commit=c), "commit": c} for k, (u, c, _) in SOURCES.items()}
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
    elif failures:
        print(f"\n{failures} file(s) differ from data/MANIFEST.json. Do not use them for a record; "
              "please open an issue with this output.", file=sys.stderr)
        return 1
    else:
        print(f"\nall files match data/MANIFEST.json. Data is in {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
