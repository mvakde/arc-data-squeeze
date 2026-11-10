# Looped mdlARC d96 ×6

A 1.05M looped model.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 49.000 | 60.625 | 1x A100 80GB | 3.0 + 1.1 |

Parameters: 1,047,000. Training: 330 epochs on the main tier's data, 80 views at decode.

ARC-AGI-1: Older, slower code.

Not yet run on ARC-AGI-2.

Reproduce: `python launch_run.py --config specs/data_squeeze/arc1_d96x6.json` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
