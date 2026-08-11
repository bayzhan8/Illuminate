<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 0 · What this is

![A grid of small squares standing for the nonzero entries of a production
model, twenty rows deep and twenty-one columns wide. As the animation runs,
squares fade out in waves until only a small block in the upper left remains
solid.](hero.gif)

Each square is a place where a variable appears in a constraint. That is the
whole model, as written.

Watch what survives. **20 rows, 21 columns and 42 nonzeros become 7, 9 and
14.** Two thirds of the model is gone, and the answer has not changed: both
versions cost **$290**, and a solution to the small one can be turned back into
a solution to the big one exactly.

This is presolve. It is not an approximation, not a heuristic, and not
optional. Every serious solver does it, they all do it differently, and it is
one of the main reasons two solvers running "the same algorithm" are not the
same speed.

> **In one sentence.** Most of a model is usually redundant, and finding out
> which part is a separate job from solving it.

---

Chapter 0 of 10

Next: [A solver is not an algorithm](../01-not-an-algorithm/README.md)  
Contents: [solvers](../../README.md)
