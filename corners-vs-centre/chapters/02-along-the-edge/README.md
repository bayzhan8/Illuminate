<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · Along the edge

![The five-sided region with a path drawn along its boundary. The path starts
at the origin, runs along the bottom edge, then turns twice, stopping at the
corner marked in green. Each corner along the way is labelled with what the
plan is worth.](the-walk.gif)

![The same region and the same three-hop path shown as a still, with every
corner along the way labelled by the dollar value of the plan there: zero, then
320, then 340, then 350 at the final corner.](the-walk.png)

The walk rests on a fact that has to be established before it makes any sense:
if a linear program has an optimum at all, then some corner achieves it.

The reason is that the objective is linear. Stand anywhere in the region that
is not a corner and there is a direction you can move in without leaving, and
along which the objective either improves or stays level. Keep going and you
run into a wall; slide along it and repeat. You cannot get stuck partway,
because a linear objective has no interior peak to get stuck on. Whatever the
best value is, a corner attains it.

That converts an infinite search into a finite one, and the simplex method is
what you get by taking the conversion seriously:

1. Stand at a corner.
2. Look along each edge leaving it. If one of them improves the objective,
   take it to the next corner.
3. If none does, stop. You are optimal.

Step 3 is the part that makes it a *method* rather than a search. When no
adjacent corner is better, no corner anywhere is better. The check is local
and the conclusion is global, and that is the whole of what duality buys you,
worked out in [the duality guide](../lp-duality/).

On the workshop, from a standing start:

| corner | plan | worth | what has run out |
|---|---|---|---|
| 0 | build nothing | $0 | nothing |
| 1 | 10⅔ tables | $320 | finishing |
| 2 | 10 tables, 2 chairs | $340 | finishing, planks |
| 3 | 9 tables, 4 chairs | **$350** | planks, bench time |

Three hops, out of five corners. At the last one every edge leads downhill, so
it stops.

> **In one sentence.** Simplex never guesses and never searches: it stands on a
> corner, improves along an edge, and knows it is finished when no edge
> improves.

---

Chapter 2 of 10

Previous: [A new kind of problem](../01-a-new-kind-of-problem/README.md)  
Next: [It should have been slow](../03-it-should-have-been-slow/README.md)  
Contents: [corners-vs-centre](../../README.md)
