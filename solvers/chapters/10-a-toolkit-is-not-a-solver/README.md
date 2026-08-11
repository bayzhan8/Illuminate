<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · A toolkit is not a solver either

There is a third thing a name can refer to, and it causes more confusion than
either of the first two, because it contains both.

**Google OR-Tools** is where this gets misread. OR-Tools is a toolkit, not a
solver. Inside it are Google's own engines, **GLOP** for linear programming and
**PDLP** for very large ones, alongside wrappers that let it drive SCIP, HiGHS
and the commercial solvers. "We used OR-Tools" does not say which engine solved
anything.

The exception is **CP-SAT**, which is Google's own and is a genuinely different
kind of machine. It is a constraint programming solver built on a SAT engine: it
works in whole numbers, learns clauses from the conflicts it hits, and does not
lean on a linear relaxation the way a MIP solver does. It has won its category
at the MiniZinc competition repeatedly. For scheduling, rostering and
assignment, where the constraints are logical rather than numerical, it is often
the right tool and it will beat an LP-based solver comfortably.

Its limits are the mirror image. It wants integers and bounded variables. Give
it genuinely continuous quantities, or a model whose strength lives in its
linear relaxation, and a MIP solver is the better answer.

> **In one sentence.** "We used OR-Tools" names a toolkit rather than an
> engine, and the one engine in it worth choosing deliberately is CP-SAT.

---

Chapter 10 of 14

Previous: [When the problem is not linear](../09-not-linear/README.md)  
Next: [Why the benchmarks cannot be read straight](../11-the-benchmarks/README.md)  
Contents: [solvers](../../README.md)
