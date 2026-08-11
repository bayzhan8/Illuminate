<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · Why simplex is the wrong shape

The simplex method walks from corner to corner of the feasible region, and each
step is a chain:

1. Work out which product would improve the plan if you started making it.
2. Work out how much of it you can make before some rule binds.
3. Update the plan, and update the bookkeeping that made step 1 answerable.

You cannot start step 1 of the next iteration until step 3 of this one has
finished, because step 3 is what changes the answer to step 1. The dependency
is not incidental to the implementation; it *is* the method. Each corner is
chosen using the information produced at the previous corner.

There is a second problem underneath. The bookkeeping in step 3 is a
factorisation of the current basis, maintained incrementally, and solving with
it is a triangular solve: a sequence of substitutions where each one needs the
previous result. Sparse triangular solves have very little parallelism in them
by construction.

None of this makes simplex a bad method. It is an extremely good method, and on
most problems it is still the one to use. It is simply the wrong shape for a
machine whose advantage is doing ten thousand independent things at once.

*(Why interior point methods are a different shape again, and where each one
wins, is [the guide before this one](../corners-vs-centre/).)*

> **In one sentence.** Simplex is a chain of dependent decisions, so its speed
> comes from taking few steps rather than from taking them in parallel.

---

Chapter 2 of 10

Previous: [Wider, not faster](../01-wider-not-faster/README.md)  
Next: [A method made of one operation](../03-one-operation/README.md)  
Contents: [lp-on-gpu](../../README.md)
