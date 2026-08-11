<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · Why the benchmarks cannot be read straight

The obvious move is to look up which solver is fastest. The standard source is
Hans Mittelmann's benchmark pages, which have run for years and are the closest
thing the field has to a referee.

Read them, and read the note at the top first.

Results for **IBM CPLEX and FICO Xpress were removed** after those vendors
objected, following the 2018 INFORMS annual meeting. **Gurobi withdrew in August
2024.** **MindOpt followed in December 2024.** The pages are still valuable and
still run, but the leaderboard now shows the solvers that stayed, and the
absence of a name is not information about its speed.

That is the first problem. The second is worse and applies to every benchmark
ever published: **a benchmark is a set of models, and yours is not in it.**
Solver performance varies over instances by orders of magnitude. A solver that
wins on a shifted geometric mean over a public set can be the slower one on your
particular model, and the only way to find out is to run yours.

Which is not hard, and is the actual advice. Take ten instances that look like
what you will be solving, run every candidate on them with a fixed time limit,
and compare. That measurement is worth more than every published table put
together, because it is measuring the thing you care about.

Two traps while you do it. Compare like with like: a solver that returns a
0.01% gap has not done the same work as one that proved optimality. And solve
each model more than once, because most solvers are deterministic only when
their thread count is fixed, and a concurrent run will give you different
timings and sometimes different optimal solutions on repeat runs of the same
input.

> **In one sentence.** The public tables are missing most of the commercial
> field by request, and even complete they would not be about your model.

---

Chapter 8 of 10

Previous: [A layer is not a solver](../07-a-layer-not-a-solver/README.md)  
Next: [The licence is the deployment problem](../09-the-licence/README.md)  
Contents: [solvers](../../README.md)
