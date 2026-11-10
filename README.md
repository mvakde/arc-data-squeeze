# ARC Data Squeeze

**How high can you score on ARC-AGI when the data is fixed to the ~1,300 public, human-made ARC tasks?**

Train from scratch on one fixed set of tasks. Use any architecture and any amount of compute. Score on the public
ARC-AGI-1 and ARC-AGI-2 evaluation sets. LLMs, pretrained weights and outside data are not allowed. It is the
[NanoGPT slowrun](https://github.com/qlabs-eng/slowrun) idea applied to ARC: when data is the limit, how much can a
model squeeze out of it?

The launch entries are small looped transformers. At 19M parameters they score **71.9% on ARC-AGI-1** and **13.9%
on ARC-AGI-2**, and the 8.4M version trains in about 2 H200-hours.

## Current records

Top-2 / oracle, %. Each tier is one table; every entry reports both benchmarks. The less data a tier allows, the
harder it is.

| Tier | Training data | ARC-AGI-1 | ARC-AGI-2 |
| --- | --- | --- | --- |
| [**+ReARC**](#rearc) | ARC-AGI-1 + ARC-AGI-2 + ConceptARC + ReARC examples | **81.38** / 88.00 | **20.14** / 32.08 |
| [**Main**](#main) | ARC-AGI-1 + ARC-AGI-2 + ConceptARC | **71.88** / 81.50 | **13.89** / 20.56 |
| [**ARC-only**](#arc-only) | ARC-AGI-1 + ARC-AGI-2 | open | open |

Main is the headline tier. All records so far are single seeds, so treat gaps of a few points as noise
(see [FAQ](FAQ.md#how-noisy-is-a-single-run)).

## Rules in one minute

Full text: [RULES.md](RULES.md).

1. **Fixed data.** Train only on what `prepare_data.py` builds for your tier and benchmark. Generic augmentation of
   that data (rotations, reflections, colour permutations, scaling) is fine. Generated puzzles, other datasets,
   text and code are not.
2. **Transductive protocol.** You may train on the evaluation tasks' demo pairs and use their test inputs. You may
   never use their test outputs. `prepare_data.py` withholds them, including under task IDs shared between ARC-AGI-1
   and ARC-AGI-2.
3. **From scratch.** Start from random weights. No LLMs or pretrained models anywhere in the pipeline. You can use
   them as coding assistants.
4. **Anything else goes:** any architecture, compute, test-time training or decoding. Report the parameter count
   and GPU-hours.
5. **Both benchmarks.** Train one model on the ARC-AGI-1 set and one on the ARC-AGI-2 set with the same method, and
   report both.
6. **Score:** official top-2 accuracy, ranked. Also report the oracle, the share of test inputs where the answer
   is anywhere among your ≤100 candidates.

## Quick start

```bash
git clone https://github.com/mvakde/arc-data-squeeze.git && cd arc-data-squeeze
python prepare_data.py                                   # Main tier; --tier arc-only | rearc | all
python score.py --benchmark arc1 submission.json --candidates candidates.json.gz
```

`prepare_data.py` needs only Python 3.9+ and its standard library. It downloads ARC-AGI-1, ARC-AGI-2 and ConceptARC at
pinned commits and writes `data/<tier>/<benchmark>/challenges.json` (train on this) and `solutions.json`
(scoring only). It then checks every file's SHA-256 and counts against [`data/MANIFEST.json`](data/MANIFEST.json).

| Tier | Benchmark | Tasks | Training pairs | Test inputs (outputs withheld) |
| --- | --- | ---: | ---: | ---: |
| Main | ARC-AGI-1 | 1,307 | 5,445 | 419 |
| Main | ARC-AGI-2 | 1,307 | 5,697 | 167 |
| ARC-only | ARC-AGI-1 | 1,147 | 4,538 | 419 |
| ARC-only | ARC-AGI-2 | 1,147 | 4,790 | 167 |
| +ReARC | either | Main + 401,589 pairs on the 400 ARC-AGI-1 training tasks | | |

To train the baseline, follow [baseline/README.md](baseline/README.md).

## Submit

1. Run your method on both benchmarks. Save each run's `submission.json` (ARC Prize format) and, for the oracle,
   its candidates.
2. Add a folder `records/<tier>/<YYYY-MM-DD>_<name>/` with a `README.md`, a `record.json` and the predictions.
3. Check it with `python score.py --verify records/<tier>/<YYYY-MM-DD>_<name>`.
4. Open a pull request that adds only that folder.

Records need public code at a commit and weights for at least one seed. Non-record entries are welcome too,
for example small models or new ideas. Details: [SUBMITTING.md](SUBMITTING.md).

## Leaderboards

Top-2 / oracle, %, mean over seeds; bold marks the tier record. `—`: not run on that benchmark yet. GPU-hours are
training plus decoding for one run (ARC-AGI-1, then ARC-AGI-2 where they differ). The launch entries come from the
[write-up](https://mvakde.github.io/blog/looped-mdlarc/)'s runs; every one includes its predictions, so
`python score.py --verify records/<tier>/<folder>` re-scores it.

### Main

ARC-AGI-1 + ARC-AGI-2 + ConceptARC.

| Entry | Params | Seeds | ARC-AGI-1 | ARC-AGI-2 | GPU-hours per run |
| --- | ---: | ---: | --- | --- | --- |
| [Looped mdlARC d384 ×6, scale aug, guards, likelihood ranking](records/main/2026-11-10_looped-mdlarc-d384x6-scale-guards-likelihood) | 18.9M | 1 | **71.88** / 81.50 | — | 6.8 H100/H200 |
| [Looped mdlARC d256 ×6, dropout 0.2](records/main/2026-11-10_looped-mdlarc-d256x6-dropout02) | 8.4M | 1 | 68.50 / 76.13 | — | 2.2 H200 |
| [Looped mdlARC d384 ×6](records/main/2026-11-10_looped-mdlarc-d384x6) | 18.9M | 1 | 68.38 / 79.62 | **13.89** / 20.56 | 4.6 H100, 4.4 H200 |
| [Looped mdlARC d256 ×6](records/main/2026-11-10_looped-mdlarc-d256x6) | 8.4M | 2 | 64.13 / 76.69 | — | 3.0 H100 |
| [Looped mdlARC d144 ×6](records/main/2026-11-10_looped-mdlarc-d144x6) | 2.0M | 1 | 55.63 / 68.00 | — | 4.7 A100 |
| [Looped mdlARC d96 ×6](records/main/2026-11-10_looped-mdlarc-d96x6) | 1.05M | 1 | 49.00 / 60.63 | — | 4.1 A100 |
| [Looped mdlARC d96 ×6, FFN 296](records/main/2026-11-10_looped-mdlarc-d96x6-ffn296) | 0.99M | 1 | 41.50 / 55.88 | — | 1.5 H200 |
| [Looped mdlARC d256 ×8](records/main/2026-11-10_looped-mdlarc-d256x8) | 8.5M | 1 | — | 12.64 / 18.89 | 4.1 H200 |

### ARC-only

ARC-AGI-1 + ARC-AGI-2, no ConceptARC.

| Entry | Params | Seeds | ARC-AGI-1 | ARC-AGI-2 | GPU-hours per run |
| --- | ---: | ---: | --- | --- | --- |
| *Open. The first entry sets the record.* | | | | | |

### +ReARC

Main plus the pre-generated [ReARC](https://github.com/michaelhodel/re-arc) examples for the 400 ARC-AGI-1
training tasks (pinned file, no new generation).

| Entry | Params | Seeds | ARC-AGI-1 | ARC-AGI-2 | GPU-hours per run |
| --- | ---: | ---: | --- | --- | --- |
| [Looped mdlARC d384 ×6 + ReARC, scale aug, guards, likelihood ranking](records/rearc/2026-11-10_looped-mdlarc-d384x6-rearc) | 18.9M | 1 | **81.38** / 88.00 | **20.14** / 32.08 | 10.5 H200, 9.9 H200 |

### Reference points (not re-run under these rules)

| Entry | Params | ARC-AGI-1 | ARC-AGI-2 | Note |
| --- | ---: | --- | --- | --- |
| TRM ([Jolicoeur-Martineau, 2025](https://arxiv.org/abs/2510.04871)) | 7M + per-puzzle embeddings | 44.6 | 7.8 | top-2 only, as reported |
| HRM ([Wang et al., 2025](https://arxiv.org/abs/2506.21734)) | 27M + per-puzzle embeddings | 40.3 | 5.0 | top-2 only, as reported by TRM |

## Why this benchmark

ARC-AGI measures how well a system learns a new task from a few demos. It does not limit pretraining, so a model
post-trained on millions of synthetic puzzles can score high without telling you how efficiently it learns. Data
Squeeze fixes the data, so the score measures what a method gets out of the same ~1,300 tasks. Fixing data rather
than compute keeps the GPU-poor in the game: one small model run is enough to compete.

## Links

- Write-up: [Looped mdlARC](https://mvakde.github.io/blog/looped-mdlarc/)
- Baseline code: [mvakde/mdlARC](https://github.com/mvakde/mdlARC)
- Baseline weights: [Kaggle model mithilavakde/mdlarc](https://www.kaggle.com/models/mithilavakde/mdlarc)
- Questions and proposals: [issues](https://github.com/mvakde/arc-data-squeeze/issues)

Cite with [CITATION.cff](CITATION.cff). Licence: [MIT-0](LICENSE). The ARC-AGI, ConceptARC and ReARC data keep
their own licences; this repo only downloads them.
