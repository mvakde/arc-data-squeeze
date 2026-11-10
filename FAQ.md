# FAQ

### Why fix the data instead of the compute?

ARC-AGI already limits what a model sees per task. It does not limit what it sees before, and synthetic data
pipelines can make a score say more about the data than the learner. Fixing the data asks how much a method can
learn from the same human-made tasks. Leaving compute open means one good idea on one GPU can still set a record.

### Why three tiers?

They separate what the data contributes from what the method contributes. ARC-only is the hardest, because it has
the least data. Main adds ConceptARC: 160 small, human-made concept tasks, which is the set most ARC papers train
on. +ReARC adds about 400,000 generated examples of the ARC-AGI-1 training tasks. With ReARC, the baseline's best
recipe scores 81.4 on ARC-AGI-1 against 71.9 without, although the two runs also differ in a few smaller settings.

### Why must I report both benchmarks?

Reporting only the benchmark where a method shines hides how it generalises. ARC-AGI-2 is much harder than ARC-AGI-1,
and methods rank differently on the two. Training twice costs twice the compute, but it keeps every number in its
usual meaning. There is no combined score: a row is a record if it beats either column.

### Why train separate models for ARC-AGI-1 and ARC-AGI-2?

ARC-AGI-2's training set contains 376 of the 400 ARC-AGI-1 evaluation tasks with their answers. One model trained on
everything would have seen ARC-AGI-1's answers. Each benchmark's build therefore withholds exactly its own
evaluation answers.

### Can I use the evaluation tasks' test inputs?

Yes, at test time and for anything. Only the test outputs are off limits.

### Can I use rotations, colour permutations, upscaling, …?

Yes, any transform that treats every task alike. It must not be written for particular tasks.

### Can I use a DSL, program search or hand-written checks?

Yes, if they are task-agnostic and you list them under `declared_components`. Rules or primitives written for
particular tasks are not allowed.

### Can I use an LLM?

Only as a coding assistant. LLMs and pretrained models may not appear in training, data generation or inference.

### Why is the oracle reported but not ranked?

It shows whether a method fails to find the answer or fails to pick it, and it is useful for research. Ranking it
would reward producing many guesses, so it is capped at 100 distinct candidates and never ranked.

### How noisy is a single run?

Quite noisy. Two seeds of the 8.4M baseline scored 66.25 and 62.00 on ARC-AGI-1, a gap of 4.25 top-2 points; d384
seeds differ by about one point. On ARC-AGI-2 each task is 0.83 points. Treat single-seed gaps of a few points as
noise. Three seeds make a record solid.

### How much compute does the baseline need?

The 8.4M model (d256 ×6) trains in about 1.8 hours on an H200 and decodes in about 20 minutes, so about 2 H200-hours
per benchmark. The 18.9M model (d384 ×6) takes about 4 hours on an H100 and decodes in 20 to 35 minutes.

### Why not a time-to-target speedrun?

That needs fixed hardware and someone to re-time every entry. Fixed data needs neither, and anyone can re-score a
predictions file on a laptop in a second.

### The evaluation answers are public. What stops cheating?

Records publish their code at a commit, the exact command, the weights and the predictions. Anyone can re-decode
from the weights or re-train from the code, and an entry that cannot be reproduced is removed. This is the same
trust model as the NanoGPT speedrun and Parameter Golf.

### Are near-duplicate tasks removed?

Tasks are deduplicated only by ID. Near-duplicates under different IDs were not checked. If you find one that
crosses into an evaluation set, please open an issue.

### Will there be harder tiers?

Probably. The next step down would be each benchmark with only its own data, for example ARC-AGI-1 trained on
ARC-AGI-1 alone. That tier opens once the current ones have strong entries.

### Is this connected to the ARC Prize competition on Kaggle?

No. This challenge uses the public evaluation sets only and needs no Kaggle account.
