<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 0 · What this is

![The same five-sided region drawn twice over. A blue path hugs the boundary,
hopping between corners in three straight segments. A red curve starts near the
middle of the region and sweeps smoothly through the interior, never touching a
wall, and both finish at the same marked point.](two-routes.gif)

A workshop makes tables and chairs. It has 44 planks, 30 hours of labour and
32 hours of saw time. A table takes 4 planks, 2 hours of labour and 3 of saw
time, and earns $30. A chair takes 2 planks, 3 hours of labour and 1 of saw
time, and earns $20. It is the same workshop, with the same numbers, as
[the duality guide](../lp-duality/).

Draw every plan the workshop could legally carry out — so many tables across, so
many chairs up — and they fill the shaded region above. Each straight edge is one
of the limits running out: along one edge there are no planks left, along
another no labour. The **corners** are where two limits run out at the same
moment, and the **walls** are the edges themselves. Nobody chose that shape. It
is simply what is left once each limit has taken its cut.

The best the workshop can do is **9 tables and 4 chairs, worth $350**, and both
routes drawn above arrive at it. They have almost nothing else in common.

The blue route only ever stands at corners. It hops from one to the next, three
times, and stops. The red route never stands at a corner and never even touches
a wall; it curves through the middle of the region and stops because it got
close enough, not because it arrived anywhere.

That difference is not a detail of implementation. The two methods disagree
about where the answer to a linear program *lives* — one says at a corner, the
other says at the end of a curve through open space — and nearly everything in
this guide, including which method your solver runs on which problem, follows
from that disagreement.

> **In one sentence.** Two methods, one answer, and no shared idea about where
> a solution lives.

---

Chapter 0 of 14

Next: [A new kind of problem](../01-a-new-kind-of-problem/README.md)  
Contents: [corners-vs-centre](../../README.md)
