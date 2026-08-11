<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 13 · Where this leaves things

The honest summary is narrow and worth stating precisely.

For linear programs large enough that forming and storing a factorisation is
the binding constraint, a method whose entire inner loop is matrix-vector
products is a genuinely different proposition, and hardware built for bandwidth
suits it. That is a real and important class of problem, and it was previously
not solvable at all.

For everything else, the established methods remain established for good
reasons: problems where a factorisation fits comfortably, problems needing
high accuracy, problems that are really integer programs wanting a basis at
every node. The chapters above are most of those reasons.

What has actually changed is that the answer to "which algorithm" now depends
on the machine, in a way it did not for thirty years.

The specific benchmark numbers in this area move quickly, and none are quoted
here, because a guide that dates in six months is worse than one that does not
try. The primary sources, if you want the current state: the PDLP paper by
Applegate and co-authors, the cuPDLP line of work, and Mittelmann's benchmark
pages, which are updated continuously.

---

Chapter 13 of 13

Previous: [What it costs](../12-what-it-costs/README.md)  
Contents: [lp-on-gpu](../../README.md)
