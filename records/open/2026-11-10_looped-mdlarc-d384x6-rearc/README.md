# Looped mdlARC d384 ×6 + ReARC, scale augmentation, deterministic filters, likelihood ranking

d384 ×6 looped transformer trained on ARC-AGI, ConceptARC and up to 1,000 ReARC examples per ARC-AGI-1 training task, with scale augmentation; decoded with scale views, deterministic filters and likelihood ranking.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the public [mdlARC](https://github.com/mvakde/mdlARC) `reproduction` branch at `aba27ca` carries the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 81.375 | 88.000 | 1x H200 NVL | 9.4 + 1.1 |
| ARC-AGI-2 | 42 | 20.139 | 32.083 | 1x H200 NVL | 9.3 + 0.6 |

Parameters: 18,900,000. Training: 330 epochs on the challenge data plus ReARC, 80 views at decode.

ARC-AGI-1: plain votes, without filters or likelihood ranking, score 78.75.

Beyond the rules (listed in the Open table, not a record):

- Scale augmentation: integer block upscaling of every grid in a training sequence, and scale views at decode.
- Deterministic filters (transductARC's "symbolic guards"): task-agnostic checks that reject candidates whose colours or shape contradict the demos.
- ReARC data: up to 1,000 pre-generated examples per ARC-AGI-1 training task, 129 known-bad pairs removed.

Reproduce: `python launch_run.py --config specs/paper/rearc_and_scale/arc1_d384x6_rearc.json (arc2_d384x6_rearc.json for ARC-AGI-2)` in mdlARC at commit `aba27cacc21a9aeb47a0b29ad899b2b2f3240f72`. Weights: to be published.
