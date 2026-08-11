<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · A layer is not a solver

This is the distinction that causes the most confusion, and it is worth getting
straight before you compare anything.

You write a model in something. That something is usually not a solver.

**Modelling layers** let you write a model once and send it to any of several
engines: Pyomo, PuLP and python-mip in Python, JuMP in Julia, and the commercial
languages AMPL and GAMS. Switching solvers becomes a one-line change, which is
the strongest practical argument for using one: it makes the solver decision
reversible.

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

> **In one sentence.** Write through a modelling layer so the solver stays a
> choice, and know whether the thing you named is a layer, an engine, or both.

---

Chapter 7 of 10

Previous: [Who is who](../06-who-is-who/README.md)  
Next: [Why the benchmarks cannot be read straight](../08-the-benchmarks/README.md)  
Contents: [solvers](../../README.md)
