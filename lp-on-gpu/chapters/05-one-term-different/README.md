<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · One term different

Here is the fix, and it is almost nothing.

When the prices react, do not show them the plan's current position. Show them
where the plan is *heading*: the new plan, plus the step it has just taken,
again.

If the plan moved from `x` to `x′`, the prices are shown `2x′ − x`. That is the
cheapest imaginable guess at the next position: assume it keeps going the way
it was going.

![The same trajectory in the same plane, now winding inward toward the answer
in a tightening spiral.](inward.png)

Same problem, same step sizes, same starting point, one changed term. The
spiral reverses. After 90 steps it is 0.36 away instead of 13.1.

Side by side, from the same start, it is not a subtle difference:

![Two planes side by side, each tracing a path from the same starting point.
On the left the path winds outward and leaves the frame. On the right it winds
inward and settles on the answer.](spiral.gif)

This is the **primal-dual hybrid gradient** method, and it is the algorithm
underneath the first-order LP solvers that run on GPUs.

Its per-iteration cost is unchanged: still two matrix-vector products, still no
factorisation. It has not become a more expensive method. It has become a
convergent one.

> **In one sentence.** Letting the prices anticipate the plan's next move
> rather than react to its last one turns the spiral inward, at no extra cost.

---

Chapter 5 of 10

Previous: [The obvious version does not work](../04-the-obvious-version/README.md)  
Next: [It turns fast and shrinks slowly](../06-fast-turn-slow-shrink/README.md)  
Contents: [lp-on-gpu](../../README.md)
