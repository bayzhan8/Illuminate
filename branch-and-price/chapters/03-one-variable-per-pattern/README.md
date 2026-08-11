<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · One variable per pattern

So model the decision differently. Instead of *which pieces go on which board*,
decide **how many boards to cut with each pattern.**

Every pattern is a way of cutting a board that is already legal — the pieces
fit, by construction. So the model has nothing left to say about fitting. It
only has to say that enough pieces come out:

> **choose** how many boards to cut with each pattern, to **minimise** the
> total number of boards, so that for each length, the pieces produced across
> all patterns **cover the order**.

Relax *that* — allow a fractional number of boards cut with a pattern — and the
answer is **6.5 boards.**

The two relaxations describe the same order and differ enormously, and the
reason is worth stating plainly. Integrality was not thrown away this time; it
was **absorbed into the variables**. Every pattern is a whole-board decision
that has already been made correctly, so relaxing the count of patterns never
un-decides it. What is left to relax is much less damaging.

| | says you need at least | so, at least | true answer |
|---|---|---|---|
| the obvious model, relaxed | 5.44 boards | 6 | 7 |
| one variable per pattern, relaxed | **6.5 boards** | **7** | 7 |

The second relaxation is tight enough to settle the question on its own here.
That is what makes the rest of this worth doing.

---

← [The obvious model, and why it is too weak](../02-the-obvious-model/README.md) · [all chapters](../..#chapters) · [Too many to write down](../04-too-many-to-write-down/README.md) →
