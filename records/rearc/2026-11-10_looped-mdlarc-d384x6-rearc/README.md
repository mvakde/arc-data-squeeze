# Looped mdlARC d384 ×6 + ReARC, scale augmentation, guards, likelihood ranking

The Main-tier record recipe trained with up to 1,000 ReARC examples per ARC-AGI-1 training task.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The predictions come from the write-up's runs, made with the research code; the tagged [mdlARC](https://github.com/mvakde/mdlARC) release reproduces the recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 81.375 | 88.000 | 1x H200 NVL | 9.4 + 1.1 |
| ARC-AGI-2 | 42 | 20.139 | 32.083 | 1x H200 NVL | 9.3 + 0.6 |

Parameters: 18,900,000. Training: 330 epochs on the rearc tier's data, 80 views at decode.

ARC-AGI-1: Plain votes score 78.75.

Declared components: Symbolic guards from transductARC: task-agnostic checks that reject candidates whose colours or shape contradict the demos.

Reproduce: `python launch_run.py --config specs/paper/ (ReARC recipe)` in mdlARC at tag `v3.1-nov2026`. Weights: to be published.
