# Submitting a result

A submission is a pull request that adds one folder. Maintainers then update the README tables.

## 1. Build the data and run your method

```bash
python prepare_data.py                    # it must end with "all files match"
```

Train one model per benchmark on `data/main/<benchmark>/challenges.json`, then predict the test inputs of the
evaluated tasks. These are the tasks with a `test` list in `challenges.json`, and the same IDs as
`solutions.json`. For each run, write:

- **`submission.json`**, in the ARC Prize format, with two attempts per test input, in order. This is required.

  ```json
  {"00576224": [{"attempt_1": [[3, 2], [7, 8]], "attempt_2": [[0, 0], [0, 0]]}]}
  ```

- **`candidates.json.gz`**, the ranked candidates per test input, used for the oracle. This is optional but
  expected. Either `{task_id: [[grid, grid, ...], ...]}` or the looped mdlARC baseline's own `candidates.json.gz`.
  Only the first 100 distinct grids per test input count.

Score each run:

```bash
python score.py --benchmark arc1 runs/arc1-seed0/submission.json --candidates runs/arc1-seed0/candidates.json.gz
```

## 2. Make the record folder

```
records/<track>/<YYYY-MM-DD>_<short-name>/       <track>: main, or open for the Open table
  README.md                 what is new, how to reproduce, compute, anything unusual
  record.json               the machine-readable entry (below)
  arc1/seed0/submission.json
  arc1/seed0/candidates.json.gz
  arc1/seed0/train.log      optional; strip personal paths and tokens
  arc2/seed0/...
```

`record.json`:

```json
{
  "name": "Looped transformer, d384 x6",
  "authors": ["Your Name"],
  "github": ["your-handle"],
  "track": "main",
  "date": "2026-11-10",
  "rules_version": 1,
  "params": 18900000,
  "summary": "One line: what is new.",
  "code": {
    "url": "https://github.com/you/repo",
    "commit": "full 40-character SHA",
    "command": "exact command(s) that train and decode one run"
  },
  "weights": "URL of the weights for at least one seed",
  "declared_components": [],
  "results": {
    "arc1": {
      "runs": [{"seed": 0, "top2": 71.875, "oracle": 81.5, "dir": "arc1/seed0"}],
      "top2_mean": 71.875,
      "compute": {"hardware": "1x H100 80GB", "train_gpu_hours": 4.1, "decode_gpu_hours": 0.6},
      "settings": "anything benchmark-specific, e.g. epochs"
    },
    "arc2": {
      "runs": [{"seed": 0, "top2": 13.889, "oracle": 20.556, "dir": "arc2/seed0"}],
      "top2_mean": 13.889,
      "compute": {"hardware": "1x H200", "train_gpu_hours": 4.1, "decode_gpu_hours": 0.3}
    }
  }
}
```

- `top2` and `oracle` are percentages as `score.py` prints them.
- `declared_components` lists every data source and hand-written component beyond the rules ([RULES.md](RULES.md),
  sections 1 and 2). It must be empty for a record; Open entries list what they add.
- List every seed you ran with the final recipe.
- If you only ran one benchmark, set the other to `null`. The entry is accepted, but a record should have both.

## 3. Verify and open the pull request

```bash
python score.py --verify records/main/2026-11-10_my-entry
```

This re-scores every run against the withheld outputs and checks the claimed numbers and the required fields.
A GitHub Action runs the same check on your pull request. Fill in the pull request template and say which
record, if any, you beat.

## What maintainers check

- `score.py --verify` passes.
- The code at the given commit runs the given command, and the data, priors and protocol follow [RULES.md](RULES.md).
- For records: the weights load and, where feasible, a re-decode reproduces the predictions. Top entries are
  re-trained when compute allows.
