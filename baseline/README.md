# Baseline: looped mdlARC

The baseline is a small transformer whose middle blocks are applied several times, a "loop". It is trained from
scratch on one tier's data, with deep supervision on every loop pass. It decodes each test input under 80
augmented views and votes for the top two answers. The [write-up](https://mvakde.github.io/blog/looped-mdlarc/)
explains the method and its ablations.

Code: [mvakde/mdlARC](https://github.com/mvakde/mdlARC) at tag `v3.1-nov2026`
<!-- TODO before announcing: replace with the tag link and the full commit SHA once the tag exists. -->
(commit `TODO`). The tag carries one spec per configuration below in `specs/data_squeeze/`.

## Run it

```bash
git clone --branch v3.1-nov2026 https://github.com/mvakde/mdlARC.git && cd mdlARC
pip install -r requirements.txt
python dataset_building_scripts/download_and_group.py
python launch_run.py --config specs/data_squeeze/arc1_d256x6.json      # ARC-AGI-1, Main tier, 8.4M
```

The launcher builds the Main-tier data itself, from the same pinned sources as `prepare_data.py`, with the same
tasks and pairs. To train on a file from this repo instead, copy
`data/<tier>/<benchmark>/{challenges,solutions}.json` into `mdlARC/assets/` and set `"skip_data_build": true` in
the spec. For the ARC-only tier, set `"add_conceptarc": false` in the spec's `dataset` block.

A finished run writes `runs/<run_name>/` with `submission.json` (ARC Prize format), `candidates.json.gz`,
`score.json` and `oracle_score.json`. Both prediction files go straight into a record folder and `score.py`.

## Configurations

Single seeds, 330 epochs, 80 views. Top-2 / oracle, %.

| Spec | Params | ARC-AGI-1 | ARC-AGI-2 | Time per run |
| --- | ---: | --- | --- | --- |
| `arc1_d256x6` | 8.4M | 66.25 / 77.25 (seed 42), 62.00 / 76.12 (seed 43) | — | ~1.8 h train + ~20 min decode on an H200 |
| `arc1_d384x6`, `arc2_d384x6` | 18.9M | 68.38 / 79.62 | 13.89 / 20.56 | ~4 h train + 20–35 min decode on an H100 or H200 |
| `arc2_d256x8` | 8.5M | — | 12.64 / 18.89 | |
| `arc1_d144x6` | 2.0M | 55.63 / 68.00 | — | |
| `arc1_d96x6` | 1.05M | 49.00 / 60.62 | — | |

The record-setting recipes add scale augmentation, symbolic guards and likelihood ranking (Main, 71.88), and ReARC
(+ReARC, 81.38). Their specs are in `specs/paper/`. Expect a seed spread of a few points. See the
[FAQ](../FAQ.md#how-noisy-is-a-single-run).
