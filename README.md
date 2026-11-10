# ARC Data Squeeze

**How high can a model score on ARC-AGI when trained from scratch only on the ~1,300 public, human-made ARC tasks?**

## Why

The official ARC-AGI benchmarks measure sample efficiency inside a puzzle: a few demos, then the test. They allow
unlimited pretraining, so language models post-trained on huge synthetic sets can score arbitrarily high, and the
score no longer says how efficiently anything was learned.

Data Squeeze fixes the data and measures data efficiency across puzzles: how much can a model learn from the same
~1,300 tasks? It is similar in spirit to OpenAI's Parameter Golf and the NanoGPT Slowrun. The 8.4M baseline takes
about 2 H200-hours, so it is open to the GPU-poor.

## Rules (v0)

These are first-draft rules and open to feedback: please open an issue.

1. **From scratch.** Train from random initialisation. No pretrained weights.
2. **Allowed data.** The public ARC-AGI-1 and ARC-AGI-2 tasks, deduplicated by task ID, plus ConceptARC. Nothing
   else: no text or code corpora, and no LLM- or program-generated ARC data.
3. **Evaluation tasks.** For the benchmark being scored, its evaluation tasks' demo pairs may be used in training,
   but never their test outputs (the transductive protocol of mdlARC, HRM and TRM). This holds wherever the same task
   ID appears: for example, ARC-AGI-2's training set contains 376 of the 400 ARC-AGI-1 evaluation tasks.
4. **+ReARC.** A separate "+ReARC" column may be reported. It is not the main score.
5. **Anything else goes.** Any architecture, any compute. Report the parameter count
   and the training cost.

## Scoring

- **Benchmarks:** ARC-AGI-1 public evaluation (400 tasks) and ARC-AGI-2 public evaluation (120 tasks).
- **Main score:** top-2 accuracy, the official metric. Two attempts per test input; a task with several test inputs
  gets partial credit.
- **Also report the oracle:** the right grid is anywhere among all your candidates. The gap between the two shows
  whether a model fails to find the answer or fails to pick it.

## Data

The baseline builds one training set per benchmark. Counts are demo pairs (input and output grids).

| | ARC-AGI-1 runs | ARC-AGI-2 runs |
| --- | --- | --- |
| Training set of the evaluated benchmark | 400 ARC-1 training tasks (1,718 pairs) | 1,000 ARC-2 training tasks (4,308 pairs) |
| Other ARC set, not already included | 347 ARC-2 tasks (1,457 pairs) | 27 ARC-1 tasks (123 pairs) |
| ConceptARC (Moskvichev et al., 2023) | 160 tasks (907 pairs) | 160 tasks (907 pairs) |
| Evaluated tasks, demos only | 400 tasks (1,363 pairs; 419 test outputs withheld) | 120 tasks (359 pairs; 167 withheld) |
| **Pairs per epoch** | **5,445** | **5,697** |
| Tasks | 1,307 | 1,307 |

773 task IDs are shared between ARC-1 and ARC-2; near-duplicates under different IDs were not checked.

## Leaderboard v0

Seed entries come from the looped mdlARC write-up. Each is trained from scratch on the set above for 330 epochs and
decoded with 80 views; one seed per row unless noted. "Top-2 only" means no oracle was logged.

### ARC-AGI-1 (400 evaluation tasks)

| Entry | Parameters | Top-2 / oracle (%) | Compute |
| --- | --- | --- | --- |
| Looped mdlARC, d384 ×6, + scale augmentation, guards, likelihood ranking | 18.9M | **71.88 / 81.50** | not reported |
| Looped mdlARC, d384 ×6 | 18.9M | 68.38 / 79.62 | not reported |
| Looped mdlARC, d256 ×6 | 8.4M | 66.25 / 77.25 (seed 42); 62.00 / 76.12 (seed 43) | ~2 H200-hours (train + decode) |
| Looped mdlARC, d144 ×6 | 2.0M | 55.625 / 68.00 | not reported |
| Looped mdlARC, d96 ×6, FFN 320 | 1.05M | 49.00 / 60.62 | 3 h 46 min on one A100, incl. 57 min decode (older, slower code) |
| TRM, reported in its paper, not re-run under these rules | 7M network + 430M per-puzzle embeddings | 44.6 (top-2 only) | ~3 days on 4×H100 |

### ARC-AGI-2 (120 evaluation tasks)

| Entry | Parameters | Top-2 / oracle | Compute |
| --- | --- | --- | --- |
| Looped mdlARC, d384 ×6 | 18.9M | **13.89% / 20.56%** | not reported |
| Looped mdlARC, d256 ×8 | 8.5M | 12.64% / 18.89% | not reported |
| TRM, reported in its paper, not re-run under these rules | 7M network + embeddings | 7.8% (top-2 only) | not reported |

### +ReARC (separate column, not the main score)

| Entry | Parameters | ARC-AGI-1 | ARC-AGI-2 |
| --- | --- | --- | --- |
| Looped mdlARC, d384 ×6, + ReARC, scale augmentation, guards, likelihood ranking | 18.9M | 81.38 / 88.00 | 20.14% / 32.08% |

This run turned on several changes at once, so ReARC's own effect is not isolated.

Scale augmentation, symbolic guards and likelihood ranking come from transductARC and are described in appendix D.4
of the write-up.

## Build the data and train the baseline

Code: [mdlARC](https://github.com/mvakde/mdlARC) (`main`, tag `v3-nov2026`).

Baseline code (looped mdlARC, same as mdlARC `main` at tag `v3-nov2026`): `baseline/mdlarc/`

```bash
git clone https://github.com/mvakde/mdlARC.git
cd mdlARC
python dataset_building_scripts/download_and_group.py   # ARC-1, ARC-2, ConceptARC (and RE-ARC) at pinned commits

# ARC-AGI-1 set: 5,445 pairs per epoch
python dataset_building_scripts/build_datasets.py --style pretrain --dataset arc1 --add-conceptarc --add-filtered

# ARC-AGI-2 set: 5,697 pairs per epoch
python dataset_building_scripts/build_datasets.py --style pretrain --dataset arc2 --add-conceptarc --add-filtered
```

This writes `assets/challenges.json` (training tasks, plus the evaluation tasks without their test outputs) and
`assets/solutions.json` (the withheld outputs, for scoring only). Training and decoding are described in the branch's
README.

## Submit a result

Open a GitHub issue or pull request with:

- the benchmark, top-2 score and oracle score;
- the parameter count;
- the compute: hardware and hours, for training and decoding;
- a link to the code (and weights, if you can share them).

## Links

- Blog: https://mvakde.github.io/blog/looped-mdlarc/
- Code: https://github.com/mvakde/mdlARC
- Weights: https://www.kaggle.com/models/mithilavakde/mdlarc

## License

[MIT-0](LICENSE).
