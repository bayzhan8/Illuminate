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

The reason is that the profit is linear: walk along any straight line and it
changes at a constant rate, rising steadily, falling steadily, or staying flat,
but never bending. (The quantity being maximised is called the **objective**,
and here it is the profit.)

That is what rules out getting stuck. Stand anywhere in the region that is not a
corner. There is always a direction you can move in without leaving the region
along which the profit does not go down, so take it, and keep going until you
run into a wall; then slide along the wall and repeat. Nothing can strand you
partway, because a quantity that only ever changes at a constant rate has no
hilltop in the middle of the region to stand on. So whatever the best value is,
some corner attains it.

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
| 1 | 10⅔ tables | $320 | saw time |
| 2 | 10 tables, 2 chairs | $340 | saw time, planks |
| 3 | 9 tables, 4 chairs | **$350** | planks, labour |

Three hops, out of five corners. At the last one every edge leads downhill, so
it stops.

> **In one sentence.** Simplex never guesses and never searches: it stands on a
> corner, improves along an edge, and knows it is finished when no edge
> improves.

---

Chapter 2 of 14

Previous: [A new kind of problem](../01-a-new-kind-of-problem/README.md)  
Next: [It should have been slow](../03-it-should-have-been-slow/README.md)  
Contents: [corners-vs-centre](../../README.md)
