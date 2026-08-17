<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · Klee and Minty build a cube

![A logarithmic chart of pivots taken against the dimension of the cube. A
dashed grey line counts the corners the cube has. A red line for the greedy rule
runs just below it, one pivot short at every size. A blue line climbs more
gently and a green line stays flat at one.](cube.png)

Victor Klee and George Minty presented their answer at a 1969 symposium; it
appeared in print in 1972, under the title *How good is the simplex algorithm?*
The answer was: in the worst case, not good.

Their construction is a cube in *n* dimensions that has been squashed, so that
its faces tilt slightly instead of meeting at right angles. It has 2ⁿ corners,
exactly as a cube should. It is not degenerate, not badly scaled by any
standard anybody had, and not in any visible way a trick.

Step 2 of the walk left something open: when more than one edge leaving a corner
improves the profit, which do you take? That choice is a separate ingredient of
the method, and it has a name — the **pivot rule**. Dantzig's original one is
greedy: take the edge that improves the profit fastest per unit of the thing
being increased.

Run the walk on the cube with that rule and it visits **every single corner**
before it stops. This repository's simplex, in exact rational arithmetic,
confirms it: the cube in 10 dimensions has 1024 corners and takes **1023
pivots**. Exactly 2ⁿ − 1, at every size tested.

The squashing is what does it. The tilt makes the greedy rule prefer the
direction of fastest immediate improvement over the direction that would
actually get somewhere, at every corner, all the way around the cube. The rule
is not being stupid; it is being exactly as greedy as it was designed to be,
against a shape built to punish greed.

You can check the claim off the chart rather than taking it on trust, and the
easiest place is the left-hand end. At dimension 3 the cube has 2³ = 8 corners,
which is where the dashed line sits. The red line sits at 7. Standing on 8
corners takes 7 hops between them, so a walk one pivot short of the corner count
is a walk that missed nothing. Read across at any dimension you like and the
gap stays exactly one: at dimension 10, 1024 and 1023.

> **In one sentence.** The worst case is real, it is exponential, and it is not
> a pathological or degenerate input.

---

Chapter 4 of 14

Previous: [It should have been slow](../03-it-should-have-been-slow/README.md)  
Next: [The rule, not the method](../05-not-the-rule/README.md)  
Contents: [corners-vs-centre](../../README.md)
