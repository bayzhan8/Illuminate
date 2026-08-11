<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · Asking for a pattern is a knapsack

The question is whether some unwritten pattern yields more than one board's
worth at these prices.

Do not search the list. *Build* the answer.

Fill one 25-foot board so as to maximise the total value of the pieces taken
off it, at the current prices. That is a knapsack problem: small, fast,
entirely standard. And its answer is the best pattern in existence at these
prices, including every one nobody has written down.

At the prices above the knapsack returns **four 4-foot pieces and one
9-foot piece**, worth 4×(1/6) + 1×(1/2) = **7/6**. More than one board, so
that pattern is missing and it goes into the model.

Pricing is where the work happens, and note what it returns: the argmax over
every column, or a proof that none is worth adding, rather than a shortlist to
sift through afterwards. When
the knapsack's best is worth **1 or less**, nothing anywhere would help, and
the restricted model is optimal for the full one.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/08.html)**
Set the three prices by hand and watch which pattern the knapsack builds.

> **In one sentence.** Finding the missing column is a knapsack, and it returns
> the best pattern in existence or a proof that none would help.

---

Chapter 8 of 11

Previous: [The same test, from the other side](../07-the-same-from-the-dual/README.md)  
Next: [The loop, and why it is allowed to stop](../09-the-loop/README.md)  
Contents: [branch-and-price](../../README.md)
