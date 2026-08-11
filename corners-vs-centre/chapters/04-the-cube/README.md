<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · Klee and Minty build a cube

![A three-dimensional cube drawn in perspective, slightly squashed so that its
faces are no longer square, with a path threading through every one of its
eight corners in turn before reaching the far one.](cube.png)

Victor Klee and George Minty presented their answer at a 1969 symposium; it
appeared in print in 1972, under the title *How good is the simplex algorithm?*
The answer was: in the worst case, not good.

Their construction is a cube in *n* dimensions that has been squashed, so that
its faces tilt slightly instead of meeting at right angles. It has 2ⁿ corners,
exactly as a cube should. It is not degenerate, not badly scaled by any
standard anybody had, and not in any visible way a trick.

Run the walk on it with Dantzig's original rule, which enters the column that
improves the objective fastest per unit, and it visits **every single corner**
before it stops. This repository's simplex, in exact rational arithmetic,
confirms it: the cube in 10 dimensions has 1024 corners and takes **1023
pivots**. Exactly 2ⁿ − 1, at every size tested.

The squashing is what does it. The tilt makes the greedy rule prefer the
direction of fastest immediate improvement over the direction that would
actually get somewhere, at every corner, all the way around the cube. The rule
is not being stupid; it is being exactly as greedy as it was designed to be,
against a shape built to punish greed.

> **In one sentence.** The worst case is real, it is exponential, and it is not
> a pathological or degenerate input.

---

Chapter 4 of 10

Previous: [It should have been slow](../03-it-should-have-been-slow/README.md)  
Next: [The rule, not the method](../05-not-the-rule/README.md)  
Contents: [corners-vs-centre](../../README.md)
