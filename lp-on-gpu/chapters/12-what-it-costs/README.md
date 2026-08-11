<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 12 · What it costs

Two costs, and they are the reason this has not replaced anything.

![Two panels. On the left, the worst rule violation falling from about a plank
to zero over a few thousand iterations, against a line marking that every
simplex iterate is exactly legal. On the right, a tied optimum where the exact
method returns a corner and the first-order method returns the
midpoint.](cost.png)

**The plan is not legal until it has converged.** A simplex iterate is always
standing on a corner of the feasible region, so it is a plan you could actually
carry out at every step. A first-order iterate approaches feasibility from
*outside*. Ten iterations in, this one proposes a plan overrunning a shelf by
0.84 planks and claims to be worth **$352.44**, more than the true optimum,
because it is cheating. It is worth more than any legal plan for the plain
reason that it is not one: it is spending planks the workshop does not have.

That is not a rounding error, it is a category difference. Stopping simplex
early gives you a legal plan that might not be the best. Stopping this early
gives you a number that is not an answer to your question at all.

**And it does not return a corner.** Take a problem where a whole edge is
optimal, every point on it equally good. The exact method returns one of the
two corners. The first-order method returns the middle.

Both are optimal, so for reporting a number it makes no difference. But branch
and bound needs a corner: it needs a *basis* to warm-start the next node from,
and a point in the middle of an edge does not give it one. Which is why
first-order methods have transformed how very large linear programs get solved,
and have so far changed integer programming much less.

> **In one sentence.** You trade a legal answer at every step, and a corner at
> the end, for an inner loop that a wide machine can actually feed.

---

Chapter 12 of 13

Previous: [Does it get the right answer?](../11-the-same-answer/README.md)  
Next: [Where this leaves things](../13-where-this-leaves-things/README.md)  
Contents: [lp-on-gpu](../../README.md)
