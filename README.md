# ARC Data Squeeze

**A new sample-efficiency benchmark: train from scratch on a tiny, fixed dataset (~2M tokens) and score as high as possible on the ARC-AGI public evaluation sets.**

Current SOTA: **70.25% on ARC-AGI-1 and 15.14% on ARC-AGI-2**, by looped mdlARC v3 at 19M parameters. Can we beat GPT-6 Astra?

Today's AI methods are sample-inefficient: they need far more examples than a person to learn something new. That matters more every year. Compute is growing much faster than the supply of good data, so getting to far more capable systems will take methods that learn more from each example. Making progress on that needs a way to measure it, and a small benchmark where new tricks are cheap to try.

The [NanoGPT slowrun](https://github.com/qlabs-eng/slowrun) is one such benchmark. It fixes 100M tokens of text and scores validation loss, a compression metric. Instead, Data Squeeze measures downstream performance: the model must solve the eval puzzles.

**Dataset:** all official ARC-AGI-1 and ARC-AGI-2 public tasks, plus ConceptARC: 1,307 tasks.  
Any architecture and any amount of compute allowed; no LLMs, pretrained weights or outside data.

<!-- TODO before announcing: add a figure here, e.g. one ARC task with the record scores, or the loop animation from
the write-up. -->

## Records

Top-2 / oracle, %. Top-2 is the ranked score; the oracle is reported for reference.

| Date | Entry | Params | ARC-AGI-1 | ARC-AGI-2 | Compute per ARC-AGI-1 run |
| --- | --- | ---: | ---: | --- | --- |
| Dec 2025 | [mdlARC v1](https://mvakde.github.io/blog/new-pareto-frontier-arc-agi/): plain transformer | 28M | 27.5\* | 2\* | 2.9 A100-hours, $1.80 |
| Mar 2026 | [mdlARC v2](https://mvakde.github.io/blog/44-on-arc-1/): 3D RoPE, ARC-AGI-2 tasks added | 75M | 44\* | 7\* | 2 hours on an RTX 5090, $0.67 |
| Nov 2026 | [Looped mdlARC v3](records/main/2026-11-10_looped-mdlarc-d384x6): middle blocks looped ×6, demo pairs in context, hub-and-spoke attention, likelihood ranking | 19M | **70.25** / 79.88 | **15.14** / 20.56 | 3.7 H200-hours, ~$13 † |

### Open

We also keep an Open table that relaxes the rules: interesting results that break a rule, usually hand-written knowledge or extra data. They show what the rules hold back, and they are not records.

| Date | Entry | Params | Beyond the rules | ARC-AGI-1 | ARC-AGI-2 | Compute per ARC-AGI-1 run |
| --- | --- | ---: | --- | --- | --- | --- |
| Sep 2026 | [transductARC](https://github.com/kschweig/transductARC) by Kajetan Schweighofer, built on mdlARC | 75M | Extra data: ReARC. Also scale augmentation, deterministic filters | 76\* / 83\* | 17\* / 24\* | a little over 4 H100-hours\* |
| Nov 2026 | [Looped mdlARC v3 + ReARC, scale augmentation, deterministic filters](records/open/2026-11-10_looped-mdlarc-d384x6-rearc) | 19M | Extra data: ReARC. Also scale augmentation, deterministic filters (as transductARC) | 81.38 / 88.00 | 20.14 / 32.08 | 10.6 H200-hours, ~$38 † |

The extra knowledge and data pays off. Looped mdlARC v3 score increases from 70.25% on ARC-AGI-1 to 81.38%. 

\* As reported by the authors, not re-scored here. transductARC's scores are a mean over 8 seeds, with the oracle over 48 candidates; its 8-model ensemble reports about 80 and 22. Costs are what the author paid, or † a measured H200 run priced at $3.60 per hour on Vast. For v3 that is a d384 ×6 run on the current code; the recorded run used older code (4.9 H100-hours).

## Rules

Full text: [RULES.md](RULES.md).

1. **Fixed data.** Train only on what `prepare_data.py` builds.
2. **Answers stay hidden.** You may train on the evaluation tasks' demos and use their test inputs, but never their
   test outputs.
3. **From scratch.** No LLMs or pretrained models anywhere in the pipeline. Using them as coding assistants is fine.
4. **Both benchmarks.** Train one model on the ARC-AGI-1 data and one on the ARC-AGI-2 data, with the same method.
5. **Limited inductive biases** ([below](#inductive-biases)). Anything learned goes: architecture, compute,
   test-time training, search over the model's own outputs. Report the parameter count and GPU-hours.

## Inductive biases

Hand-written knowledge about ARC raises scores easily, so the rules allow only what a person sees when first shown a task. Anything a person would have to work out from the grids' contents, the model must learn from the data.

**Allowed:**

| Inductive bias | Why a person has it | In the baseline |
| --- | --- | --- |
| **Grid layout:** each cell's position, which grid it is in, which input goes with which output, which grid is the question | A glance at the task shows it | Row-end and separator tokens; 3D rotary positions (row, column, grid); hub-and-spoke attention, where each demo attends to itself and the test input |
| **Certain whole-task symmetries:** rotating or mirroring every grid of a task the same way, swapping colours the same way in every grid, and reordering the demos | A rotated or mirrored task is the same puzzle, like turning the page; a person is told the colours have no meaning outside the puzzle; demo order carries no information | All 8 rotations and reflections and random colour swaps as training augmentation, and 80 such views of each task at test time |
| **Checking an answer by looking again** | A person re-checks an answer from another angle | Voting across the 80 views, then ranking the top 20 by the model's own likelihood |

**Examples of what is not allowed:**

- **Scaling, translation, cropping.** Upscaling every grid looks harmless but changes the contents: "move one cell" becomes "move two cells". Assuming that rules survive it is knowledge about ARC.
- **Hand-computed objects, symmetries or counts.** If a model needs them, it should learn them.
- **Checks on candidate answers**, such as deterministic filters that reject outputs whose colours or size contradict the demos.
- **DSLs, program search and symbolic solvers.**

The maintainer decides borderline cases with the same test: would a person know this before working anything out from the grids? If you are unsure, ask in an issue before building on it.

## Harder tracks to come

The challenge gets harder as it is solved: each time an entry passes 90% top-2 on ARC-AGI-1, data is removed. First ConceptARC goes. Then only each benchmark's official tasks remain: for ARC-AGI-1, its 800 tasks and no ARC-AGI-2 tasks.

## Quick start

```bash
git clone https://github.com/mvakde/arc-data-squeeze.git && cd arc-data-squeeze
python prepare_data.py
python score.py --benchmark arc1 submission.json --candidates candidates.json.gz
```

`prepare_data.py` needs only Python 3.9+. It downloads ARC-AGI-1, ARC-AGI-2 and ConceptARC at pinned commits, writes `data/main/<benchmark>/challenges.json` (train on this) and `solutions.json` (scoring only), and checks every file against [`data/MANIFEST.json`](data/MANIFEST.json). Each benchmark gets 1,307 tasks: 5,445 training pairs and 419 withheld test outputs for ARC-AGI-1, and 5,697 pairs and 167 withheld outputs for ARC-AGI-2.

To train the baseline, see [baseline/README.md](baseline/README.md).

## Submit

Add a folder `records/main/<YYYY-MM-DD>_<name>/` with a `README.md`, a `record.json` and your predictions, check it with `python score.py --verify <folder>`, and open a pull request. Records need public code at a commit and weights for one seed. Non-record entries are welcome, including interesting results for the Open table under `records/open/`. Details: [SUBMITTING.md](SUBMITTING.md). Questions: [FAQ.md](FAQ.md).

## Links

- Write-up: [Looped mdlARC](https://mvakde.github.io/blog/looped-mdlarc/)
- Baseline code: [mvakde/mdlARC](https://github.com/mvakde/mdlARC)
- Questions and proposals: [issues](https://github.com/mvakde/arc-data-squeeze/issues)

Cite with [CITATION.cff](CITATION.cff). Licence: [MIT-0](LICENSE). The ARC-AGI and ConceptARC data keep their own licences; this repo only downloads them.
