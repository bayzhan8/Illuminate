<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 9 · Profit that runs away

Two things can go wrong, and the dual has something to say about both. Here is
the first.

![A region with no upper limit and profit lines marching off it
forever.](edges.png)

If the rules leave a direction the workshop can go forever, there is no best
plan. Nothing is stopping it, so the profit is unbounded and there is no number
to report.

Now ask what the price side makes of that. An honest price list has to be a
ceiling over every plan at once, which is chapter 4. But a ceiling would have to
be a number bigger than every plan, and no such number exists. So there is no
honest price list either — not a bad one, not a loose one, none at all.

The two failures come as a pair, and it is worth stating the pairing plainly
because it is the shape the whole theory keeps taking: *the plan side runs away
precisely when the price side has nothing to offer.*

Which is also how a solver tells you. Hand it a model with a direction of escape
and it does not search forever and give up. It finds the direction, reports
unbounded, and the thing it hands back as evidence is a fact about the prices.

> **In one sentence.** Profit running away on one side is exactly the same event
> as no honest price list existing on the other.

---

Chapter 9 of 11

Previous: [The price is only local](../08-the-price-breaks/README.md)  
Next: [A plan that cannot exist](../10-no-such-plan/README.md)  
Contents: [lp-duality](../../README.md)
