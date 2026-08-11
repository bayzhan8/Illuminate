<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · The rest of the machine

Presolve is the part this guide can compute. It is not the only part, and for
mixed-integer problems it is not the largest.

**Cutting planes** are extra constraints that are true of every whole-number
solution but false for the fractional answer the relaxation just produced. Add
enough and the relaxation stops being able to lie to you. A modern solver
generates a dozen families of them, adds far more than it keeps, and spends real
effort deciding which to throw away, because a cut that does not tighten the
bound is a row you now have to carry.

**Heuristics** try to find a decent solution early, by rounding, by fixing
things and re-solving, by taking two known solutions and searching between them.
The value is not the solution. It is that a good incumbent lets the search prune
whole subtrees, and a search with no incumbent prunes nothing.

**Branching** is the choice of what to split on. It is the single most studied
knob in the subject, and the difference between a naive rule and a good one is
routinely orders of magnitude in tree size, which the [branch and
price](../branch-and-price/) guide runs into directly.

**Numerics** is the unglamorous one. Real models arrive with capacities in the
millions and yields around 0.0001, and the ratio between the largest and
smallest number in your matrix is a better predictor of trouble than its size.
Solvers scale the matrix to fight this. Every one of them has tolerances: a
number below which a value counts as zero, a violation below which a constraint
counts as satisfied. Those are not bugs, they are policy, and two solvers
disagreeing about whether your model is feasible is usually two policies
disagreeing rather than one of them being broken.

This guide computes none of that, and quoting numbers for it would mean
inventing them. What the chapter is for is the shape: when a solver is slow, the
question "which of these is going wrong" is more useful than "is my model too
big".

> **In one sentence.** Bound quality, a good early solution and sane numerics
> decide most solves, and none of them is the algorithm.

---

Chapter 6 of 14

Previous: [What it costs you](../05-what-it-costs/README.md)  
Next: [Who is who](../07-who-is-who/README.md)  
Contents: [solvers](../../README.md)
