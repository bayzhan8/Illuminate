<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · The obvious version does not work

The obvious thing is to move both at once. Push the plan down a little, push
the prices up a little, repeat.

To see what happens, shrink the problem until the whole state fits on a page:
one variable, one rule, `x = 3`. Then the state is a plan and a price, two
numbers, and the path they trace is a curve in a plane.

![A trajectory in the plane of plan against price, starting near the answer and
winding steadily outward in a widening spiral.](outward.png)

It winds outward. It starts 2.2 away from the answer and after 90 steps it is
13.1 away, and it keeps going.

The reason is visible in the update itself. The prices are told to react to the
plan `x`. But by the time they react, the plan has already moved on, so each
side is always responding to where the other one just *was*. Two players who are
each a step behind the other will circle each other forever, and the circling
grows.

On the real workshop the failure looks different but is no better. There the
clamp at zero keeps the numbers from running away, and instead the method
settles into an exact **repeating cycle of period 10**: the plan climbs to
about 17 tables, the prices spike, the plan is slammed to nothing, the prices
decay, and it begins again. The value it reports swings between **$0 and
$753**, and it never once sits at $350.

It does not diverge. It does not converge. It just keeps going.

> **In one sentence.** Two players each reacting to the other's previous move
> circle forever instead of settling.

---

Chapter 4 of 10

Previous: [A method made of one operation](../03-one-operation/README.md)  
Next: [One term different](../05-one-term-different/README.md)  
Contents: [lp-on-gpu](../../README.md)
