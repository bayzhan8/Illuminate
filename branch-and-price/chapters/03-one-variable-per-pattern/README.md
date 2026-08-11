<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · One variable per pattern

So model the decision differently. Instead of *which pieces go on which board*,
decide **how many boards to cut with each pattern.**

Every pattern is a way of cutting a board that is already legal: the pieces fit,
by construction. So the model has nothing left to say about fitting. It only
has to say that enough pieces come out:

> **choose** how many boards to cut with each pattern, to **minimise** the
> total number of boards, so that for each length, the pieces produced across
> all patterns **cover the order**.

Relax *that*, allowing a fractional number of boards cut with a pattern, and
the answer is **6.5 boards.**

Two relaxations of the same order, an enormous distance apart. Integrality was
not discarded this time. It was absorbed into the variables: every pattern
is a whole-board decision already made correctly, so relaxing the *count* of
patterns cannot un-decide it. What remains to relax does far less harm.

| | says you need at least | so, at least | true answer |
|---|---|---|---|
| the obvious model, relaxed | 5.44 boards | 6 | 7 |
| one variable per pattern, relaxed | **6.5 boards** | **7** | 7 |

Here the second relaxation settles the question by itself, which is the reason
to put up with everything that follows.

---

Chapter 3 of 9

Previous: [The obvious model, and why it is too weak](../02-the-obvious-model/README.md)  
Next: [Too many to write down](../04-too-many-to-write-down/README.md)  
Contents: [branch-and-price](../../README.md)
