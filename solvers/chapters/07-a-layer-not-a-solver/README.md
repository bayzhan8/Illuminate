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

**CVXPY** is a layer too, and a different animal, because it is not aimed at
linear and integer models at all. It is for **convex** optimisation, the larger
family that linear programming sits inside. Write a portfolio problem with a
risk term that squares, or a fitting problem with a penalty on the size of the
answer, and none of that is linear, all of it is convex, and none of the
solvers named so far will take it.

What makes CVXPY worth singling out is that it will not let you write nonsense.
It carries a rule system, **disciplined convex programming**, which checks that
what you typed is *provably* convex by construction rather than hoping. A
squared error is convex, so it passes. Multiply two variables together and it
refuses, because that expression is not convex and no amount of solver effort
would make the answer trustworthy. Most modelling layers accept whatever you
type and let something downstream fail later, usually by returning a local
answer with no warning that it is local. CVXPY stops at the door.

That is the same instinct as the presolve loop in this guide raising rather
than returning a half-reduced model, and it is the right instinct. A refusal
you can read beats a number you cannot check.

Underneath, CVXPY rewrites your problem into a standard **conic** form and
hands it to a solver built for that, which is a different set of names again:
**Clarabel**, **SCS** and **OSQP** among the open ones, MOSEK among the
commercial. It has used Clarabel as its default since version 1.5, having
replaced ECOS, which had been the default for years and had known trouble with
numerical stability at the edges. It will also drive HiGHS when what you wrote
turns out to be an ordinary linear program.

The limit is the same as the strength. CVXPY wants convexity. If your problem
genuinely is not convex, or its difficulty lives in whole-number decisions
rather than in curvature, this is the wrong tool and a MIP solver is the right
one.

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
