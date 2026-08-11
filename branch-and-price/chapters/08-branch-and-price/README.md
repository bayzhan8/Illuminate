<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · Branching, when the answer is 6.5 boards

Nobody cuts half a board. The relaxation says 6.5, and 6.5 is not a plan.

For this order, rounding up happens to be right, and for cutting stock it
nearly always is — the relaxation is famously tight, so much so that instances
where rounding up is *wrong* are rare and hard to construct. But "nearly
always" is not a proof, and rounding gives you a number rather than a set of
cuts. To get an answer you can take to the saw, the fractions have to be
branched away.

Which gives **branch-and-price**: branch-and-bound, where the relaxation at
every node is solved by column generation.

> **At each node**
>
> 1. Impose the node's branching decisions on the master.
> 2. Solve that relaxation by column generation — the full loop, at every node.
> 3. Prune if it is infeasible, or if its bound cannot beat the best plan found.
> 4. If the answer is whole, record it. Otherwise pick a fractional pattern
>    count and split: one child uses it at most ⌊x⌋ times, the other at least ⌈x⌉.

![A search tree of eleven boxes, each labelled with the number of boards its
relaxation needs, some marked whole, some cannot win, branching down four
levels.](tree.png)

Each box hides a complete solve-price-add cycle. The tree stays small because
it starts from a bound that is already nearly right — which is the payoff for
chapter 3. **Branch-and-price is branch-and-bound with a much better
relaxation, and a way of representing that relaxation implicitly.**

### Two traps, both of which cost this repository real answers

Writing this was where the theory bit back, and both failures looked completely
reasonable while producing wrong numbers, so they are worth naming.

**A branching row has a price too.** Tell a node "use this pattern at most
zero times" and that restriction gets a dual value of its own — which inflates
that one pattern's reduced cost. The knapsack then keeps nominating a pattern
the master already holds and has pinned at zero. Reading that as "no improving
column exists" stops the loop early, leaves the node's bound too high, and for
a minimisation a bound that is too high prunes away the true optimum.

**A restricted master can be infeasible at a node that is perfectly feasible.**
The columns that would have met the demand simply have not been generated yet.
Declaring the node infeasible throws away real solutions. The fix is to give
the master emergency columns at a punitive price, so it always has an answer
and can produce prices; they fall out on their own as real patterns arrive.

The first version of the solver in this folder had neither fix, and disagreed
with brute force on **476 of 1230** test instances. It now agrees on all of
them. Neither bug announced itself — the trees looked sensible and the answers
looked plausible, and only running every small instance against an independent
brute-force solver revealed it.

A last honesty note: branching on a single pattern's count, as above, is a
*weak* rule. Real implementations use Ryan–Foster branching, which branches on
whether two pieces share a board and pushes the restriction down into the
knapsack. This guide keeps the simpler rule because it is legible, and pays for
it with a bigger tree.

---

← [The loop, and why it is allowed to stop](../07-the-loop/README.md) · [all chapters](../..#chapters) · [Where this leads](../09-where-this-leads/README.md) →
