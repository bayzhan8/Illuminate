<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · What presolve takes out

Here is the model the animation was showing. Three products, two periods. For
each product and period there is how much to **make**, how much to **hold** at
the end of the period, and a yes/no switch for whether the line is **open**.

| what it says | how it is written |
|---|---|
| stock at the start is nothing | `holdA0 = 0`, one row per product |
| stock at the end is nothing | `holdA2 = 0`, one row per product |
| what came in and what went out balance | `holdA1 + makeA2 − holdA2 = demand` |
| you cannot make anything without setting up | `makeA2 − 100 × openA2 ≤ 0` |
| the factory has a capacity each period | `makeA1 + makeB1 + makeC1 ≤ 100` |

Demand is 40 units of A in period 2 and nothing in period 1, 25 units of B in
each period, and **nothing at all for product C**, which is on the sheet
because it is on the product list, not because anyone ordered it.

Every reduction below is something a person reading that model would notice.
The point is that the model, as handed over, cannot notice any of it.

**A row with one variable in it is a bound wearing a costume.** `holdA0 = 0` is
not really a constraint. It is a fact about a variable. Presolve reads it as
`0 ≤ holdA0 ≤ 0`, writes that on the column, and deletes the row. Six rows go
this way immediately, one for each product's opening and closing stock.

**A variable whose two bounds have met is not a variable.** `holdA0` now has a
lower bound of 0 and an upper bound of 0. There is nothing left to decide.
Presolve substitutes the value into every row that mentions it and removes the
column. Six columns go.

**A row already at its limit forces everything in it.** Product C's balance row
in period 2 now reads `holdC1 + makeC2 − holdC2 = 0`, with `holdC2` fixed at
zero and the other two unable to go below zero. The smallest the left side can
be is zero, and zero is exactly what it must equal. So *every* variable in that
row is pinned at the only value that works. Nobody ordered any C, so nobody
makes any C, and now the model knows.

**A row that cannot be violated is not a constraint.** The capacity row for
period 2 allows 100 units. After the reductions above, the most that the
surviving variables can add up to in that row is less than 100, whatever they
do. The row can never bite. It is deleted.

**A row can also just narrow a variable.** The balance row for A in period 2
says `holdA1 + makeA2 = 40`. Both are at or above zero, so neither can exceed
40. Nothing is fixed and nothing is deleted, but two columns are now boxed in,
and that turns out to matter enormously in the next chapter.

**Whole numbers round.** If a variable has to be an integer and its bounds are
now 0.25 and 0.75, there is no value left and the model is infeasible. If its
bounds are 0.25 and 1, then it is really 1.

*(The names are **singleton row**, **fixed column**, **forcing row**,
**redundant row**, **bound tightening** and **integer rounding**. Real solvers
run dozens more, including ones that spot two rows saying the same thing and
ones that prove a variable can be moved to a bound without loss.)*

> **In one sentence.** Each reduction is something obvious, and the model as
> written has no way to see any of them.

---

Chapter 2 of 10

Previous: [A solver is not an algorithm](../01-not-an-algorithm/README.md)  
Next: [The cascade, and where the gap opens](../03-the-cascade/README.md)  
Contents: [solvers](../../README.md)
