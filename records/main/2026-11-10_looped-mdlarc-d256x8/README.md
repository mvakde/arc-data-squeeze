# Looped mdlARC d256 ×8

d256 with the middle blocks looped 8 times.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-2 | 42 | 12.639 | 18.889 | 1x H200 NVL | 3.8 + 0.3 |

Parameters: 8,500,000. Training: 330 epochs on the main tier's data, 80 views at decode.

Not yet run on ARC-AGI-1.

Reproduce: `python launch_run.py --config specs/data_squeeze/arc2_d256x8.json` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
