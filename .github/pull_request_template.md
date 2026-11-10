<!-- One pull request adds one folder: records/<track>/<YYYY-MM-DD>_<name>/. See SUBMITTING.md. -->

**Entry:** <!-- name, one line on what is new -->
**Track:** <!-- main / open -->
**Record?** <!-- which record it beats, on which benchmark, or "non-record entry" -->

| Benchmark | Seeds | Top-2 (mean) | Oracle (mean) | Params | GPU-hours (train + decode, per run) |
| --- | ---: | ---: | ---: | ---: | --- |
| ARC-AGI-1 | | | | | |
| ARC-AGI-2 | | | | | |

**Code:** <!-- repo URL @ full commit SHA, and the exact command -->
**Weights:** <!-- URL, at least one seed for a record -->

### Checklist

- [ ] `python prepare_data.py` ended with "all files match", and I trained only on that data (Open entries: anything else is in `declared_components`).
- [ ] No evaluation test outputs were used in training, tuning, test-time training, decoding or selection.
- [ ] No LLMs, pretrained models or outside data in training, data generation or inference.
- [ ] Every seed run with the final recipe is reported.
- [ ] Main: only the inductive biases in RULES.md section 2. Open: everything beyond the rules is listed in `declared_components`.
- [ ] `python score.py --verify records/<track>/<folder>` passes.
- [ ] The pull request adds only my record folder; logs contain no personal paths or tokens.
