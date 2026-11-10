# FAQ

### Why fix the data instead of the compute?

ARC-AGI measures how well a system learns a new task from a few demos. It does not limit what a model sees before
that, and a model trained on millions of synthetic puzzles can score high without telling you how efficiently it
learns. Fixing the data asks how much a method can learn from the same human-made tasks. Leaving compute open means
one good idea on one GPU can still set a record.

### Why these tasks?

ARC-AGI-1, ARC-AGI-2 and ConceptARC are the human-made tasks, and the set most ARC papers train on. Generated
examples such as ReARC are left out, so the score says what a method learns from tasks people designed. Harder tracks
open as the challenge is solved (see RULES.md, section 1).

### What is the Open table?

A place for interesting results that break a rule, usually with extra data or hand-written knowledge. They show what
the rules hold back: the baseline model gains 11 points on ARC-AGI-1 from ReARC, scale augmentation and
deterministic filters. They are not records.

### Which augmentations can I use?

The 8 rotations and reflections, colour permutations, and reordering or subsetting demos. Anything else, such as
upscaling, translation or cropping, is not allowed for a record (see RULES.md, section 2).

### Can I use a DSL, program search or hand-written checks?

Not for a record. A result that uses them can go in the Open table if you list them under `declared_components`.

### Can my architecture find objects, symmetries or counts?

If it learns them, yes. If you compute them by hand from the cell colours, that is not allowed for a record.

### Can I use the evaluation tasks' test inputs?

Yes, at test time and for anything. Only the test outputs are off limits.

### Why must I report both benchmarks?

Reporting only the benchmark where a method shines hides how it generalises. ARC-AGI-2 is much harder than ARC-AGI-1,
and methods rank differently on the two. There is no combined score: a row is a record if it beats either column.

### Why train separate models for ARC-AGI-1 and ARC-AGI-2?

ARC-AGI-2's training set contains 376 of the 400 ARC-AGI-1 evaluation tasks with their answers. One model trained on
everything would have seen ARC-AGI-1's answers. Each benchmark's build therefore withholds exactly its own
evaluation answers.

### Can I use an LLM?

Only as a coding assistant. LLMs and pretrained models may not appear in training, data generation or inference.

### Why is the oracle reported but not ranked?

It shows whether a method fails to find the answer or fails to pick it, which is useful for research. Ranking it
would reward producing many guesses, so it is capped at 100 distinct candidates and never ranked.

### How noisy is a single run?

Quite noisy. Two seeds of an 8.4M baseline scored 66.25 and 62.00 on ARC-AGI-1, a gap of 4.25 top-2 points; d384
seeds differ by about one point. On ARC-AGI-2 each task is 0.83 points. Treat single-seed gaps of a few points as
noise. Three seeds make a record solid.

### How much compute does the baseline need?

About 4 hours of training on one H100 or H200 per benchmark, plus 20 to 35 minutes of decoding.

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

### Is this connected to the ARC Prize competition on Kaggle?

No. This challenge uses the public evaluation sets only and needs no Kaggle account.
