<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · The cascade, and where the gap opens

Take those reductions one at a time and they are unremarkable. Run them in a
loop and something else happens.

![Two panels, each plotting how much of a model is left against how many rounds
of the reduction loop have run. Three stepped lines fall away in each: nonzeros,
columns and rows. Neither panel drops all at once; both keep stepping down for
many rounds.](cascade.png)

If presolve were a checklist applied once, those lines would fall in round one
and go flat. They do not. The small model takes **13 rounds** to settle and the
larger one takes **27**.

The reason is that each reduction is what makes the next one visible. Deleting a
row creates a fixed column. Fixing a column empties a row. Emptying a row
narrows a bound. Narrowing a bound fixes another column.

None of those steps is clever. What is doing the work is the loop: a reduction
that was invisible in round one becomes obvious in round nine, because eight
rounds of other reductions have cleared the view. That is why presolve is
described as a fixed point rather than a pass, and why a solver keeps going
until a whole round changes nothing.

It is also why two solvers with the same list of reductions can end up with
models of different sizes. Run them in a different order and you reach a
different fixed point.

> **In one sentence.** Presolve is a loop rather than a checklist, because each
> reduction is what exposes the next one.

---

Chapter 3 of 14

Previous: [What presolve takes out](../02-what-it-removes/README.md)  
Next: [A decision made by arithmetic](../04-a-decision-by-arithmetic/README.md)  
Contents: [solvers](../../README.md)
