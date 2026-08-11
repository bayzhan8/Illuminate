# Design notes: what solvers actually do

## Who it is for

Somebody who can already model a problem and has met a solver, and who has
either been surprised by one being slow or been stopped by one being difficult
to deploy. No background in solver internals is assumed. The reading level is
the same as the rest of the repository: a strong first-year undergraduate.

## The problem this topic had that the others did not

Every other guide here explains one mathematical idea, and the repository rule
that every quoted number is computed by the code beside it works cleanly.

Half of this topic is not mathematics. "Which solver is fastest", "what does a
licence cost", "can this run in a container" are questions about products, and
the answers change. That is a real tension with the house standard, and the
decision taken here is to split the guide rather than fudge it:

* **Chapters 1 to 5** are computed. There is a presolve engine in `src/`, it
  runs on a real model, and every number in those chapters comes out of it.
* **Chapters 6 to 10** are not computable, and say so. Claims are dated
  ("checked in August 2026"), attributed, and restricted to things that have
  been stable for years. No benchmark leaderboard is quoted.

The precedent for the second half is the `lp-on-gpu` guide, which refuses to
quote benchmark numbers on the grounds that a guide dating in six months is
worse than one that does not try. The same policy applies here.

## Why presolve is the computable spine

It was the obvious candidate before anything was written, and it survived the
test of actually building it:

* it is genuinely where a large share of solver performance lives, so the
  chapter is not a toy standing in for the real subject
* it is exactly the kind of code that returns confident wrong answers, which
  makes it a good fit for the repository's two-independent-routes habit
* the cascade is visual. A model shrinking round by round is a picture, not a
  diagram of labelled boxes
* it is under-taught relative to its importance, which is the gap this
  repository exists to fill

## Finding the instance

The rule is to find the example by computation before writing prose, and it
mattered here. The requirements were:

* small enough to draw as a matrix, so around twenty rows
* realistic, and specifically *badly written* in the ordinary way: opening and
  closing stock as constraints rather than bounds, a product on the sheet that
  nobody ordered, a capacity row that cannot bind
* a long cascade rather than one big drop, since the cascade is the argument
* something left to solve afterwards. A model presolve annihilates completely
  makes a worse point than one it halves
* at least one reduction that settles a decision a reader would consider real

The lot-sizing model at three products and two periods satisfies all of these:
20 rows, 21 columns, 42 nonzeros down to 7, 9 and 14 over thirteen rounds, with
`openB1` forced to 1 in round 9 by bound tightening and integer rounding. That
last one is the chapter, and it was found by running the engine and reading the
log rather than by designing it in.

An eight-product, six-period version is kept for the scale panel and is never
printed.

## What is deliberately not here

* **No benchmark table.** See above. Chapter 8 explains why the public ones are
  harder to read than they look, which is more durable than any snapshot.
* **No claim about which solver is fastest.** The guide says to measure on your
  own instances, because that is the true answer and the only one that will
  still be true next year.
* **No cutting planes, heuristics or branching rules in code.** Chapter 5
  describes them and explicitly says nothing there is computed. Implementing a
  credible cut separator would double the topic and duplicate what
  `branch-and-price` already does with a search tree.
* **Only three figures.** Chapters 6 to 10 get tables, because their content is
  categorical. A chart of invented numbers would be worse than a table of real
  ones.

## The verification

`test_solvers.py` runs presolve on 400 random small models and checks the
result against enumerating every whole point in the box. That catches the
failure that matters: a reduction that removes the optimum. It also checks that
postsolve rebuilds a point that is feasible *for the original model*, which is
a different claim from the reduced model being solved correctly.

The loop refuses rather than guessing. If the reductions have not settled after
`MAX_ROUNDS`, `presolve` raises instead of returning a half-reduced model, on
the same principle as the value-function reconstruction in `lp-duality`.

## Where it sits in the sequence

Last of the linear-programming chain, after `lp-duality`, `corners-vs-centre`,
`lp-on-gpu` and `branch-and-price`. It refers back to all four and assumes the
reader knows what a relaxation and a search tree are.
