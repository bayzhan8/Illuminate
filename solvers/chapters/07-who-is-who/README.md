<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · Who is who

The landscape splits cleanly, and the split is about money rather than
mathematics.

**The commercial solvers.** Gurobi, IBM CPLEX, FICO Xpress, COPT and MOSEK.
They are genuinely fast, they are supported, and on hard mixed-integer models
the good ones remain ahead of everything free. They are also expensive, and
priced per machine or per core in ways that interact badly with autoscaling.
Every one of them has a free size-limited or academic tier.

**The open-source solvers.** These are the ones worth knowing:

| solver | what it is | licence |
|---|---|---|
| **HiGHS** | LP, MIP and QP. Simplex, interior point and a first-order method. The serious default | MIT |
| **SCIP** | Constraint-integer programming. Very strong on hard MIPs, extremely hackable | Apache 2.0 since 8.0.3 |
| **CBC** and **Clp** | The old COIN-OR pair. Still everywhere, largely because everything already depends on them | EPL |
| **GLPK** | Small, old, GNU. Fine for teaching, slow for work | GPL |
| **cuOpt** | NVIDIA's GPU engine for LP, MIP and routing | Apache 2.0 |
| **Clarabel**, **SCS**, **OSQP** | Conic and quadratic. What the convex problems of chapter 7 get sent to | Apache 2.0 / MIT |

Two changes here matter more than any benchmark. SCIP moved from an academic
licence to **Apache 2.0** at version 8.0.3, which turned it from something you
could publish papers with into something you could ship. And **HiGHS** has become
good enough to be the default answer for anyone who does not have a specific
reason to pay, which was not true a decade ago.

The honest summary of the gap: for pure linear programs at ordinary sizes, the
free solvers are close enough that the difference rarely decides anything. For
hard mixed-integer models the commercial ones are still meaningfully ahead, and
the harder your model, the more that is true.

> **In one sentence.** HiGHS or SCIP unless you have a hard integer model and a
> budget, and the reasons to pay are narrower every year.

---

Chapter 7 of 14

Previous: [The rest of the machine](../06-the-rest-of-the-machine/README.md)  
Next: [A layer is not a solver](../08-a-layer-not-a-solver/README.md)  
Contents: [solvers](../../README.md)
