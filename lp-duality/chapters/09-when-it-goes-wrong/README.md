<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 9 · When it goes wrong

Two things can go wrong, and the dual has something to say about both.

![Two panels. On the left, a region with no upper limit and profit lines
marching off it forever. On the right, a scale of tables showing that the planks
reach eleven and the order starts at twelve, with nothing in
between.](edges.png)

**Profit that runs away.** If the rules leave a direction the workshop can go
forever, there is no best plan. A ceiling would have to be a number bigger than
every plan, and there is no such number — so there are no honest prices at all.
The two failures come as a pair: *the plan side runs away exactly when the price
side has nothing to offer.*

**A plan that cannot exist.** Suppose an order arrives for 12 tables. Forty-four
planks make eleven tables, so the order cannot be met. Here is the part worth
seeing — the impossibility has a *short proof*, and the proof is arithmetic
rather than an exhausted search:

> Take a quarter of the plank rule, and all of the order.
> Add them together, and they say: half of the chairs, at most −1.
> A count of chairs cannot be negative. So there is no such plan.

Four lines, checkable by anyone, and it settles the question forever. This is
the same idea as a price list, wearing different clothes: a weighted mixture of
the rules that adds up to something plainly absurd. It is called a **Farkas
certificate**, and the fact that one always exists when a system is impossible
is the fact that strong duality is built on.

There is one more case worth naming so it does not surprise you: at a bend in
that curve from chapter 8, the price is genuinely not unique. Standing exactly
at 45 ⅐ planks, one more plank is worth nothing and one fewer costs $6.25, and
both numbers are legitimate prices. A solver will hand you one of them without
mentioning the other. This is called **degeneracy**, and it is why a
sensitivity report should always be read as a range and never as a point.

---

Chapter 9 of 10

Previous: [The price is only local](../08-the-price-breaks/README.md)  
Next: [Where this leads](../10-where-this-leads/README.md)  
Contents: [lp-duality](../../README.md)
