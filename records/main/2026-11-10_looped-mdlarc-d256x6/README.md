# Looped mdlARC d256 ×6

The 8.4M quick-start baseline: d256 ×6 looped transformer with deep supervision.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 66.250 | 77.250 | 1x H100 80GB (seed 42), 1x H200 NVL (seed 43) | 2.6 + 0.4 |
| ARC-AGI-1 | 43 | 62.000 | 76.125 | 1x H100 80GB (seed 42), 1x H200 NVL (seed 43) | 2.6 + 0.4 |

Parameters: 8,400,000. Training: 330 epochs on the main tier's data, 80 views at decode.

ARC-AGI-1: Seed 42's predictions are a re-decode of its final checkpoint that saved candidates (same top-2 and oracle as the first decode). Seed 43 ran on later code with a faster decoder.

Not yet run on ARC-AGI-2; the ARC-AGI-2 8.5M entry is d256 ×8.

Reproduce: `python launch_run.py --config specs/data_squeeze/arc1_d256x6.json` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
