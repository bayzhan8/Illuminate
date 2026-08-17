<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 0 · What this is

![A grid of small squares standing for the nonzero entries of a production
model, twenty rows deep and twenty-one columns wide. As the animation runs,
squares fade out in waves until only a small block in the upper left remains
solid.](hero.gif)

Three words first, because the whole guide is written in them.

A **model** is a problem handed to a computer: a list of quantities to be
decided, and a list of arithmetic rules those quantities must satisfy. Write it
out as a grid — one row per rule, one column per quantity, and a mark in a
square wherever that quantity appears in that rule — and you get the picture
above. So a **row** is a rule, a **column** is a quantity to be decided, and the
marks are what people call the **nonzeros**. Almost every square is empty, which
is why models get drawn this way: real ones are overwhelmingly empty, and that
emptiness is what makes them solvable at all.

The model above is a small production plan: three products, two periods, 20
rules, 21 quantities and 42 marks.

Watch what survives. **20 rows, 21 columns and 42 nonzeros become 7, 9 and
14.** Two thirds of the model is deleted before any solving starts, and the
answer does not change: both versions cost **$290**, and an answer to the small
model can be turned back into an answer to the big one exactly.

Here is one of the deletions, so that nothing about this looks like magic. One
of the twenty rules says that the stock of product A at the start is zero. It
arrived written as a rule because that is what was convenient to type, but it is
not really a statement about how quantities interact. It is a fact about one
quantity. So the solver copies "fixed at zero" onto that column and deletes the
row; the model is one rule smaller and means exactly the same thing. And now
that the quantity is pinned, it substitutes zero everywhere that column appears
and deletes the column too. Two deletions, no cleverness, no risk.

This is **presolve**. It is not an approximation, not a heuristic and not
optional. Every serious solver does it, they all do it differently, and it is
one of the main reasons that two solvers running "the same algorithm" are
nowhere near the same speed.

> **In one sentence.** Most of a model is usually redundant, and finding out
> which part is a separate job from solving it.

---

Chapter 0 of 14

Next: [A solver is not an algorithm](../01-not-an-algorithm/README.md)  
Contents: [solvers](../../README.md)
