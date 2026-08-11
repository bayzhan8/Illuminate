<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · How to choose

The short version, in the order the questions actually arrive.

| if | then |
|---|---|
| you are learning, or the model is small | **HiGHS**, through a modelling layer |
| it is a pure LP, at almost any size | **HiGHS**; reach for a commercial solver or a first-order method only when it stops finishing |
| the model is scheduling, rostering or assignment | try **CP-SAT** before anything LP-based |
| it is convex but not linear: squares, norms, risk terms | **CVXPY**, which will pick Clarabel or SCS for you |
| it is a hard MIP and the answer is worth money | benchmark **Gurobi**, **COPT** and **Xpress** on your own instances |
| you want to hack the search itself | **SCIP** |
| it is enormous, sparse, and a rough answer is fine | a first-order method: **PDLP**, or **cuOpt** on a GPU |
| you cannot manage licence servers | anything open source, and stop worrying |

Three closing observations, which are the ones I would want to have been told.

**Modelling beats solver choice, usually by more than an order of magnitude.**
The chapters above are about a solver deleting two thirds of a model. A better
formulation does not need deleting. If a solve is too slow, rewriting the model
will usually buy you more than any solver will, and the big-M constant from
chapter 3 is the first place to look.

**Measure before you buy.** The evaluation licences exist for this. Ten of your
own instances, a fixed time limit, all candidates.

**Keep the solver replaceable.** Write through a layer, and the decision you
make today stays cheap to revisit. Everything in chapters 6 to 9 changes. SCIP's
licence changed. Gurobi left the benchmarks. cuOpt was proprietary and is now
Apache 2.0. The one durable move is to not be welded to any of it.

> **In one sentence.** Formulate well, measure on your own models, and keep the
> solver behind a layer so that none of this has to be decided permanently.

---

Chapter 10 of 10

Previous: [The licence is the deployment problem](../09-the-licence/README.md)  
Contents: [solvers](../../README.md)
