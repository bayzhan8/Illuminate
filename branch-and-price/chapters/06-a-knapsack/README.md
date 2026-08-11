<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · Asking for a pattern is a knapsack

So: is there a pattern whose pieces are worth more than one board?

Do not search the list. *Build* the answer. Fill one 25-foot board with pieces
so as to maximise their total value at the current prices. That is a knapsack
problem — small, fast, and completely standard — and its answer is the single
best pattern in existence at these prices, including the ones nobody has
written down.

At the prices above, the knapsack comes back with **four 4-foot pieces and one
9-foot piece**, worth 4×(1/6) + 1×(1/2) = **7/6**. That is more than one board.
So that pattern is missing, and it goes into the model.

The **pricing problem** is the engine of the whole method, and note what it
gives you: not a hint, not a heuristic, but the exact best column, or a proof
that none exists. When the knapsack's best is worth **1 or less**, no pattern
anywhere is worth adding, and the restricted model is optimal for the full one.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/06.html)**
Set the three prices by hand and watch which pattern the knapsack builds.

---

← [Start with a few, and let the prices ask](../05-let-the-prices-ask/README.md) · [all chapters](../..#chapters) · [The loop, and why it is allowed to stop](../07-the-loop/README.md) →
