<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 9 · When the problem is not linear

Everything named so far assumes your model is linear, or linear with some
whole-number decisions in it. Plenty of real models are neither, and they fail
at the door rather than solving slowly.

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

That is the same instinct as the presolve in this guide reporting infeasible
outright rather than handing back a half-reduced model, and it is the right
instinct. A refusal you can read beats a number you cannot check.

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

> **In one sentence.** If your model has squares or norms in it, none of the
> solvers named so far will take it, and the layer that will also refuses to
> let you write something it cannot vouch for.

---

Chapter 9 of 14

Previous: [A layer is not a solver](../08-a-layer-not-a-solver/README.md)  
Next: [A toolkit is not a solver either](../10-a-toolkit-is-not-a-solver/README.md)  
Contents: [solvers](../../README.md)
