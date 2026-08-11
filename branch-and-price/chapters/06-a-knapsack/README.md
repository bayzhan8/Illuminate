<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · Asking for a pattern is a knapsack

The question is whether some unwritten pattern yields more than one board's
worth at these prices.

Do not search the list. *Build* the answer. Fill one 25-foot board so as to
maximise the total value of the pieces taken off it, at the current prices.
That is a knapsack problem, small and standard, and its answer is the best
pattern in existence at these prices, including every one nobody has written
down.

At the prices above the knapsack returns **four 4-foot pieces and one
9-foot piece**, worth 4×(1/6) + 1×(1/2) = **7/6**. More than one board, so
that pattern is missing and it goes into the model.

Pricing is where the work happens, and note what it returns: the argmax over
every column, or a proof that none is worth adding. Not a candidate list. When
the knapsack's best is worth **1 or less**, nothing anywhere would help, and
the restricted model is optimal for the full one.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/06.html)**
Set the three prices by hand and watch which pattern the knapsack builds.

---

Chapter 6 of 9

Previous: [Start with a few, and let the prices ask](../05-let-the-prices-ask/README.md)  
Next: [The loop, and why it is allowed to stop](../07-the-loop/README.md)  
Contents: [branch-and-price](../../README.md)
