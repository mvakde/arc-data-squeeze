# Looped mdlARC d384 ×6, scale augmentation, guards, likelihood ranking

d384 ×6 looped transformer with deep supervision, trained with scale augmentation; decoded with scale views, then ranked by likelihood after transductARC's symbolic guards.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 71.875 | 81.500 | 1x H100 SXM (epochs 1-130), then 1x H200 NVL | 6.2 + 0.6 |

Parameters: 18,900,000. Training: 330 epochs on the main tier's data, 80 views at decode.

ARC-AGI-1: Likelihood ranking used a separate GPU pass that rescored the top 20 candidates; its time is not included. The attempts were rebuilt offline from the saved candidates and likelihoods.

Not yet run on ARC-AGI-2.

Declared components: Symbolic guards from transductARC: task-agnostic checks that reject candidates whose colours or shape contradict the demos.

Reproduce: `python launch_run.py --config specs/paper/ (scale augmentation + guards + likelihood recipe)` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
