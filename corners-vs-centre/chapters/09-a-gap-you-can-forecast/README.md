<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 9 · A gap you can forecast

![A logarithmic chart with mu decreasing to the right. Two nearly parallel
straight lines descend together: an upper line for the guaranteed bound and a
lower one for the gap that actually remained.](the-gap.png)

This is the property that decided real deployments, and it is not speed.

A point on the central path arrives with a receipt. The gap between what it is
worth and the best possible is at most **μ times the number of walls**. The
workshop has five walls (three rules and two floors), so the bound is 5μ:

| μ | plan | worth | promised within | actually within |
|---|---|---|---|---|
| 100 | 3.762, 4.053 | $193.92 | $500.00 | $156.08 |
| 10 | 8.408, 3.633 | $324.90 | $50.00 | $25.10 |
| 1 | 9.019, 3.870 | $347.96 | $5.00 | $2.04 |
| 0.1 | 9.004, 3.984 | $349.80 | $0.50 | $0.20 |
| 0.01 | 9.000, 3.998 | $349.98 | $0.05 | $0.02 |

Divide μ by ten and you divide your remaining ignorance by ten. Before running
anything, you can say how many more rounds buy how many more digits.

Simplex offers nothing comparable. Standing at a corner, you know what you have
and you know it is not yet optimal, but the number of hops left is not a
quantity you can ask about. Every corner looks like the ones before it right up
until the last one. That is fine when the solve takes a second. It is a
different matter when it takes six hours on a model due at 6am, and it is the
reason interior point methods took over the very large end of the market rather
than the whole of it.

> **In one sentence.** The barrier tells you how far from optimal you are while
> you are still running; the walk can only tell you once it has stopped.

---

Chapter 9 of 10

Previous: [What the barrier actually does](../08-what-the-barrier-does/README.md)  
Next: [Neither one won](../10-neither-one-won/README.md)  
Contents: [corners-vs-centre](../../README.md)
