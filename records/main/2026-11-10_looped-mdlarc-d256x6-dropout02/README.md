# Looped mdlARC d256 ×6, dropout 0.2

The 8.4M baseline with dropout raised from 0.1 to 0.2.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 68.500 | 76.125 | 1x H200 NVL | 2.1 + 0.1 |

Parameters: 8,400,000. Training: 330 epochs on the main tier's data, 80 views at decode.

Not yet run on ARC-AGI-2.

Reproduce: `python launch_run.py --config specs/data_squeeze/arc1_d256x6.json with dropout 0.2` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
