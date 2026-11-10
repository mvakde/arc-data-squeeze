# Baseline: looped mdlARC

The baseline is a small transformer whose middle blocks are applied several times, a "loop". It is trained from
scratch on the challenge data, with deep supervision on every loop pass. It decodes each test input under 80
augmented views and votes for the top two answers. The [write-up](https://mvakde.github.io/blog/looped-mdlarc/)
explains the method and its ablations.

Code: [mvakde/mdlARC](https://github.com/mvakde/mdlARC), branch `reproduction` at commit
`aba27cacc21a9aeb47a0b29ad899b2b2f3240f72`.
<!-- TODO: switch to the v3.1-nov2026 tag and its SHA once it exists, and make likelihood ranking ("inference_rescore":
true) the default in specs/data_squeeze/arc1_d384x6.json and arc2_d384x6.json. -->

## Run it

```bash
git clone --branch reproduction https://github.com/mvakde/mdlARC.git && cd mdlARC
git checkout aba27cacc21a9aeb47a0b29ad899b2b2f3240f72
pip install -r requirements.txt
python dataset_building_scripts/download_and_group.py
python launch_run.py --config specs/data_squeeze/arc1_d384x6.json      # ARC-AGI-1
python launch_run.py --config specs/data_squeeze/arc2_d384x6.json      # ARC-AGI-2
```

The record ranks the top 20 voted candidates by the model's likelihood. At this commit that is off by default: add
`"inference_rescore": true` to the spec's `eval_defaults` to switch it on.

The launcher builds the challenge data itself, from the same pinned sources and with the same tasks and pairs as
`prepare_data.py`. To train on this repo's files instead, copy `data/main/<benchmark>/{challenges,solutions}.json`
into `mdlARC/assets/` and set `"skip_data_build": true` in the spec.

A finished run writes `runs/<run_name>/` with `submission.json` (ARC Prize format), `candidates.json.gz`,
`score.json` and `oracle_score.json`. Both prediction files go straight into a record folder and `score.py`.

## Recipes

Single seeds, 330 epochs, 19M parameters. Top-2 / oracle, %.

| Entry | Recipe | ARC-AGI-1 | ARC-AGI-2 | Time per run |
| --- | --- | --- | --- | --- |
| Record | d384 ×6 with deep supervision, likelihood ranking of the top 20 voted candidates (`specs/data_squeeze/`) | 70.25 / 79.88 | 15.14 / 20.56 | ~4 h training + 20–35 min decoding on one H100 or H200 |
| Open table | the same, plus ReARC, scale augmentation, deterministic filters and likelihood ranking (`specs/paper/`) | 81.38 / 88.00 | 20.14 / 32.08 | ~9.4 h training + 0.6–1.1 h decoding on one H200 |

Expect a seed spread of a few points. See the [FAQ](../FAQ.md#how-noisy-is-a-single-run).
