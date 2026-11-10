#!/usr/bin/env python3
"""Build the ARC Data Squeeze training sets and check them against data/MANIFEST.json.

    python prepare_data.py                      # ARC-AGI-1 and ARC-AGI-2 builds
    python prepare_data.py --benchmark arc1     # one benchmark

Each build holds the ARC-AGI-1, ARC-AGI-2 and ConceptARC tasks. Writes data/main/<benchmark>/:
    challenges.json   every task you may train on, in the ARC Prize format. The evaluated benchmark's
                      tasks keep their demo pairs and test inputs; their test outputs are removed.
                      Every other task has all its pairs under "train".
    solutions.json    the withheld test outputs, for scoring only. Never train on them.

Standard library only. Upstream sources are pinned to commits. The files hold exactly the tasks and pairs of
the looped mdlARC baseline's `build_datasets.py --style pretrain` builds, so you can drop them into that code.
(That script orders the other benchmark's tasks by directory listing, which varies between machines; this one
always puts training before evaluation, so the SHA-256 checks hold everywhere.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
}
TRACK = "main"  # the folder name; harder tracks (see RULES.md) will add builds
BENCHMARKS = ("arc1", "arc2")


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


# ---------------------------------------------------------------- build

def flatten(tasks: dict) -> dict:
    """Every pair becomes a training pair: test pairs are appended to train."""
    return {tid: {"train": t["train"] + t.get("test", [])} for tid, t in tasks.items()}


def build(benchmark: str, arc: dict, concept: dict) -> dict:
    """Returns {filename: object} for one benchmark."""
    other = "arc2" if benchmark == "arc1" else "arc1"
    shared = (set(arc["arc1"]["training"]) | set(arc["arc1"]["evaluation"])) & \
             (set(arc["arc2"]["training"]) | set(arc["arc2"]["evaluation"]))
    # The other benchmark's tasks whose IDs do not appear in this one (training first, then evaluation).
    other_only = {tid: t for split in ("training", "evaluation")
                  for tid, t in arc[other][split].items() if tid not in shared}
    evaluated = arc[benchmark]["evaluation"]

    challenges = dict(flatten(arc[benchmark]["training"]))
    challenges.update(flatten(concept))
    challenges.update(flatten(other_only))
    challenges.update({tid: {"train": t["train"], "test": [{"input": p["input"]} for p in t["test"]]}
                       for tid, t in evaluated.items()})
    outputs = {"solutions.json": {tid: [p["output"] for p in t["test"]] for tid, t in evaluated.items()}}

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
    ap.add_argument("--benchmark", choices=[*BENCHMARKS, "both"], default="both")
    ap.add_argument("--out", type=Path, default=ROOT / "data", help="output root (default: data/)")
    ap.add_argument("--cache", type=Path, default=ROOT / "data" / "_downloads")
    ap.add_argument("--write-manifest", action="store_true", help="maintainers: record hashes instead of checking")
    args = ap.parse_args()

    benchmarks = list(BENCHMARKS) if args.benchmark == "both" else [args.benchmark]
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"files": {}}

    arc = {name: load_arc(name, args.cache) for name in BENCHMARKS}
    concept = load_conceptarc(args.cache)

    failures = 0
    for benchmark in benchmarks:
        outputs = build(benchmark, arc, concept)
        check_leak(outputs["challenges.json"], outputs["solutions.json"])
        folder = args.out / TRACK / benchmark
        folder.mkdir(parents=True, exist_ok=True)
        for name, obj in sorted(outputs.items()):
            blob = json.dumps(obj).encode()
            (folder / name).write_bytes(blob)
            key = f"{TRACK}/{benchmark}/{name}"
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
            print(f"{status:8} {key:30} {counts}")

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
