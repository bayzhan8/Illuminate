<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · A layer is not a solver

This is the distinction that causes the most confusion, and it is worth getting
straight before you compare anything.

You write a model in something. That something is usually not a solver.

**Modelling layers** let you write a model once and send it to any of several
engines: Pyomo, PuLP and python-mip in Python, JuMP in Julia, and the commercial
languages AMPL and GAMS. Switching solvers becomes a one-line change, which is
the strongest practical argument for using one: it makes the solver decision
reversible.

So the first question about any name you are handed is which of the two it is.
Get that wrong and you will compare a language with an engine and conclude
something about neither.

> **In one sentence.** You write a model in a layer and it is solved by an
> engine, and keeping those separate is what keeps the engine replaceable.

---

Chapter 8 of 14

Previous: [Who is who](../07-who-is-who/README.md)  
Next: [When the problem is not linear](../09-not-linear/README.md)  
Contents: [solvers](../../README.md)
