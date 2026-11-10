# Looped mdlARC d144 ×6

A 2.0M looped model.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 55.625 | 68.000 | 1x A100 80GB | 3.8 + 0.9 |

Parameters: 2,011,000. Training: 330 epochs on the main tier's data, 80 views at decode.

ARC-AGI-1: Older, slower code.

Not yet run on ARC-AGI-2.

Reproduce: `python launch_run.py --config specs/data_squeeze/arc1_d144x6.json` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
