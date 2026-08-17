<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · Start with a few

The model cannot be written down. So do not write it down. Start with a model
that is obviously too small.

Take a few patterns — say the lazy ones, each board cut into copies of a single
length — and solve *that*. Everyone calls it the **restricted master**: the
real model, restricted to the handful of patterns somebody actually bothered to
write down. It is the real problem with almost all of its variables missing.

Our order has three lazy patterns: a board cut into six 4-foot pieces, a board
cut into two 9s, a board cut into two 10s. With only those three on the table
there is nothing to decide, because each ordered length has exactly one source.
Here is the whole calculation, and it is arithmetic you can do in your head:

- Three 4-foot pieces, six to a board, is half a board of cutting.
- Six 9-foot pieces, two to a board, is three boards.
- Seven 10-foot pieces, two to a board, is three and a half.

Add them up: **7 boards**, which answers a smaller question than the one we
asked.

That number is an honest upper bound, since those three patterns really do fill
the order. What it is not is the answer to the strong model, which has three
more patterns nobody has written down, and in the mill instance four trillion.

So the method now needs one thing, and only one. Not a way to search the missing
patterns — there are too many. A way to answer *whether any of them would help*
without adding them, and ideally without looking at them.

That is what the next two chapters are, and the surprising part is that the
too-small model already contains the answer.

> **In one sentence.** Solving a deliberately impoverished model is free, and
> the only question left is whether anything is missing from it.

---

Chapter 5 of 11

Previous: [Too many to write down](../04-too-many-to-write-down/README.md)  
Next: [What the prices are telling you](../06-what-the-prices-say/README.md)  
Contents: [branch-and-price](../../README.md)
