<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · What it costs you

The reductions above changed the shape of the model. They also changed what the
model can prove about itself, and that is the part that pays.

![A number line from 240 to 298 dollars. A grey dot marks the bound the model
could prove as written, a blue dot marks the stronger bound after presolve, and
a red dot marks the true best plan, with the closed part of the gap
marked.](bound.png)

Ignore the whole-number requirement and solve what is left, and the model as
written proves the answer cannot be cheaper than **$248**. After presolve, the
same relaxation proves it cannot be cheaper than **$263**. The true answer is
**$290**.

No cutting plane was added. No node was explored. **$15 of a $42 gap closed**,
purely from columns being fixed and bounds being narrowed, and a better bound is
worth more than a faster pivot, because it prunes the tree rather than walking
it. On this instance branch and bound opens **9 nodes** on the model as written
and **5** on the reduced one. Small numbers, because it is a small model; the
mechanism is what scales.

So much for the upside. Now the bill.

**Your variables stop existing.** Ask the solver for the value of `holdA0` and
it may not have one, because that column was gone before the algorithm started.
This is what postsolve is for: it walks the reductions backwards and rebuilds a
solution to the model you handed over. Every solver does this, and it is why
you get your variable back. But if you are reading the *internal* model, or
attaching callbacks to it, you are working with something that no longer
matches what you wrote.

**Sensitivity information gets harder.** Shadow prices and ranges, the subject
of [the duality guide](../lp-duality/), are attached to rows. When a row has
been deleted as redundant, the price that comes back for it is zero, which is
correct and often not what the person asking wanted to know. Some solvers
restrict presolve automatically when you ask for a sensitivity report, and it is
worth knowing whether yours does.

**"Presolve says infeasible" is a real answer and an unhelpful one.** If the
reductions prove there is no solution, you get told at once, which is fast and
correct. What you do not get is a nice explanation, because the reasoning is a
chain thirteen rounds deep. Most solvers have a separate and much slower mode
that will find a small conflicting subset of rows for you, and it is worth
finding that flag before you need it.

**And it is occasionally slower.** On a model with little redundancy, presolve
costs time and returns nothing. Rarely, it removes structure that a later part
of the solver would have exploited. This is uncommon enough that leaving it on
is the right default, and the flag to turn it off is nonetheless the first thing
to reach for when a solver behaves inexplicably, because it tells you which half
of the machine to suspect.

> **In one sentence.** Presolve buys a stronger bound and a smaller model, and
> charges you in traceability.

---

Chapter 4 of 10

Previous: [The cascade, and where the gap opens](../03-the-cascade/README.md)  
Next: [The rest of the machine](../05-the-rest-of-the-machine/README.md)  
Contents: [solvers](../../README.md)
