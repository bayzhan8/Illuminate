<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · Asking for a pattern is a knapsack

The question is whether some unwritten pattern yields more than one board's
worth at these prices.

Searching a list of four trillion patterns is hopeless. But nobody said the
answer has to be *found*. It can be **built**.

Here is the question again, phrased as a puzzle about one board. You have 25
feet of wood in front of you and a price for each length: a 4-foot piece is
worth 1/6, a 9 is worth 1/2, a 10 is worth 1/2. Cut the board so as to make the
pieces on it worth as much as possible in total. What do you cut?

That is a **knapsack problem** — the standard name for "fill a container of
fixed size with items of known size and value, as valuably as you can" — and it
is a small, fast, thoroughly solved kind of problem. Crucially, whatever it
hands back *is* a pattern, and it is the most valuable pattern that exists at
these prices. Not the most valuable one on any list. The most valuable one, full
stop, including all the ones nobody has ever written down, because the knapsack
constructed it from the wood rather than looking it up.

At the prices above the knapsack returns **four 4-foot pieces and one
9-foot piece**, worth 4×(1/6) + 1×(1/2) = **7/6**. Seven sixths is more than
one, so by chapter 6's test that pattern is worth having, and it goes into the
model.

Notice what has just been avoided. There is no shortlist and no sampling. One
knapsack solve either hands back a best pattern in existence — this order has
two patterns tied at 7/6, and any winner will do — or, when its best comes out
at **1 or less**, proves that no pattern anywhere would help, in which case the
restricted model's answer is already the full model's answer.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/08.html)**
Set the three prices by hand and watch which pattern the knapsack builds.

> **In one sentence.** Finding the missing column is a knapsack, and it returns
> the best pattern in existence or a proof that none would help.

---

Chapter 8 of 11

Previous: [The same test, from the other side](../07-the-same-from-the-dual/README.md)  
Next: [The loop, and why it is allowed to stop](../09-the-loop/README.md)  
Contents: [branch-and-price](../../README.md)
