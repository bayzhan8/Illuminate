<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · The obvious version does not work

The obvious thing is to move both at once. Push the plan down a little, push
the prices up a little, repeat.

To see what happens, shrink the problem until the whole state fits on a page:
one variable, one rule, `x = 3`. Nothing to maximise, one shelf, one product,
and the plan simply has to hit 3. Then the state is a plan and a price, two
numbers, and the path they trace is a curve in a plane.

With one of each, both matrix-vector products of chapter 6 collapse to a single
multiplication, and the whole method is two lines. Take the step size to be 0.2
on both sides. Each iteration does:

```
new plan   =  plan  + 0.2 × price
new price  =  price − 0.2 × (plan − 3)
```

The plan is pushed in whichever direction the price is pointing. The price
rises whenever the plan is short of 3 and falls whenever it is over. The catch
is in the second line: the `plan` it reads is the old one, from before the
first line ran.

Follow it from a plan of 2 and a price of 2. The price is 2, so the plan moves
up to 2.4. The plan was 2, a unit short, so the price climbs to 2.2. Next round
the plan reaches 2.84 and the price 2.32. The plan crosses 3 on the third step
and the price *is still rising*, because the plan it is being shown is the one
from before the crossing. By the time the price notices and turns around, the
plan is at 3.77 and sailing away.

![A trajectory in the plane of plan against price, starting near the answer and
winding steadily outward in a widening spiral.](outward.png)

It winds outward. It starts 2.2 away from the answer and after 90 steps it is
13.1 away, and it keeps going.

Every lap is that same overshoot, in both directions, and each one is wider
than the last. The two sides are not fighting each other. They are each
answering a question about where the other one *was*, one step too late, and a
pair of players who are each a step behind the other will circle forever.
Nothing in the update ever notices.

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

Chapter 7 of 13

Previous: [A method made of one operation](../06-one-operation/README.md)  
Next: [One term different](../08-one-term-different/README.md)  
Contents: [lp-on-gpu](../../README.md)
