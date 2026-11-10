# Looped mdlARC d384 ×6

d384 ×6 looped transformer with deep supervision; plain votes over 80 views.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 68.375 | 79.625 | 1x H100 80GB | 4.1 + 0.5 |
| ARC-AGI-2 | 42 | 13.889 | 20.556 | 1x H200 NVL | 4.1 + 0.3 |

Parameters: 18,900,000. Training: 330 epochs on the main tier's data, 80 views at decode.

ARC-AGI-1: The candidates of this decode were not saved; its oracle (79.625) comes from the run's own oracle report.

Reproduce: `python launch_run.py --config specs/data_squeeze/arc1_d384x6.json and arc2_d384x6.json` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
