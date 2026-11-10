<!-- One pull request adds one folder: records/<tier>/<YYYY-MM-DD>_<name>/. See SUBMITTING.md. -->

**Entry:** <!-- name, one line on what is new -->
**Tier:** <!-- arc-only / main / rearc -->
**Record?** <!-- which record it beats, on which benchmark, or "non-record entry" -->

| Benchmark | Seeds | Top-2 (mean) | Oracle (mean) | Params | GPU-hours (train + decode, per run) |
| --- | ---: | ---: | ---: | ---: | --- |
| ARC-AGI-1 | | | | | |
| ARC-AGI-2 | | | | | |

**Code:** <!-- repo URL @ full commit SHA, and the exact command -->
**Weights:** <!-- URL, at least one seed for a record -->

### Checklist

- [ ] `python prepare_data.py --tier <tier>` ended with "all files match", and I trained only on that data.
- [ ] No evaluation test outputs were used in training, tuning, test-time training, decoding or selection.
- [ ] No LLMs, pretrained models or outside data in training, data generation or inference.
- [ ] Every seed run with the final recipe is reported.
- [ ] Task-agnostic hand-written components, if any, are listed in `declared_components`.
- [ ] `python score.py --verify records/<tier>/<folder>` passes.
- [ ] The pull request adds only my record folder; logs contain no personal paths or tokens.
