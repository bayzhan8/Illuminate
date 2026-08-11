<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 12 · Measure on your own models

Suppose the tables were complete. They would still not answer your question, and
this is the more important of the two problems because no amount of tidying up
fixes it.

**A benchmark is a set of models, and yours is not in it.**

Solver performance varies over instances by orders of magnitude — not by tens of
percent, by factors of a thousand. A solver that wins on a shifted geometric
mean over a public set can comfortably be the slower one on your particular
model, because your model has structure that the set does not, and structure is
what solvers exploit. The aggregate is a fact about the aggregate.

Which makes the actual advice short, and it is the only thing in this chapter
worth remembering. Take ten instances that look like what you will really be
solving, run every candidate on them with a fixed time limit, and compare. That
measurement is worth more than every published table put together, because it is
the only one measuring the thing you care about.

Two traps while you do it.

**Compare like with like.** A solver that returns a 0.01% gap has not done the
same work as one that proved optimality, and the second is doing something much
harder. Fix the gap tolerance across candidates before you time anything.

**Solve each model more than once.** Most solvers are deterministic only when
their thread count is fixed. A concurrent run will give you different timings,
and sometimes different optimal solutions, on repeat runs of the same input. If
you measure once, you are partly measuring the weather.

> **In one sentence.** The only benchmark that answers your question is ten of
> your own models with the tolerances pinned.

---

Chapter 12 of 14

Previous: [Why the benchmarks cannot be read straight](../11-the-benchmarks/README.md)  
Next: [The licence is the deployment problem](../13-the-licence/README.md)  
Contents: [solvers](../../README.md)
