# Looped mdlARC d96 ×6, FFN 296

An under-1M looped model: d96, 4 heads, FFN width 296.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 41.500 | 55.875 | 1x H200 NVL | 1.4 + 0.1 |

Parameters: 990,865. Training: 330 epochs on the main tier's data, 80 views at decode.

Not yet run on ARC-AGI-2.

Reproduce: `python launch_run.py --config specs/paper/ (0.99M recipe)` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
