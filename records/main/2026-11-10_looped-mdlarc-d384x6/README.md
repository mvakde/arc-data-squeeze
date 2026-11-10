# Looped mdlARC v3, d384 ×6

d384 ×6 looped transformer with deep supervision; 80 views, top 20 voted candidates ranked by the model's likelihood.

Launch entry from the [looped mdlARC write-up](https://mvakde.github.io/blog/looped-mdlarc/). The checkpoints were trained with the research code; the public [mdlARC](https://github.com/mvakde/mdlARC) `reproduction` branch at `aba27ca` carries the same recipe.

| Benchmark | Seed | Top-2 | Oracle | Hardware | Train + decode (h) |
| --- | ---: | ---: | ---: | --- | --- |
| ARC-AGI-1 | 42 | 70.250 | 79.875 | 1x H100 80GB | 4.1 + 0.8 |
| ARC-AGI-2 | 42 | 15.139 | 20.556 | 1x H200 NVL | 4.1 + 0.65 |

Parameters: 18,900,000. Training: 330 epochs on the challenge data. Decoding: 80 views, then the top 20 voted candidates ranked by the model's likelihood. Plain votes score 68.375 (ARC-AGI-1) and 13.889 (ARC-AGI-2).

ARC-AGI-1: Candidates from a re-decode of the same checkpoint (plain votes 68.375 / 79.875); likelihood ranking took 0.33 GPU-hours. The original decode scored 68.375 by votes.

Reproduce: python launch_run.py --config specs/data_squeeze/arc1_d384x6.json (arc2_d384x6.json for ARC-AGI-2), then the likelihood rescore of the saved candidates, as in specs/paper/rearc_and_scale/arc1_d384x6_rescore_eval.json, in mdlARC at commit `aba27cacc21a9aeb47a0b29ad899b2b2f3240f72`. Weights: to be published.
