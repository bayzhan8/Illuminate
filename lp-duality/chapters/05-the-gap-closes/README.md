<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · The gap closes, every time

So plans push up from below and price lists press down from above. The question
is whether they meet, or stop with a gap that nothing can close.

![Real plans appearing along a dollar scale from the left, and real price lists
appearing from the right, with the band of remaining possibilities shrinking
until it is a single point at three hundred and fifty
dollars.](meet.gif)

They meet. The best plan earns $350, the cheapest honest price list charges
$350, and the space between them has nothing left in it.

It would be fair to suspect this workshop of being rigged. So here are 320
more, invented at random, with different numbers of products, different numbers
of shelves and different recipes. Each was solved twice from scratch: once for
its best plan, and once, as a separate problem, for its cheapest prices.

![A scatter plot of the best plan's profit against the cheapest price list's
bill for three hundred and twenty random workshops. Every point lies on the
diagonal.](always.png)

Every point is on the diagonal. Both sides are computed in exact fractions, so
the largest disagreement across all 320 is zero. Not small. Zero.

Be clear about what that picture is, though. It is not a proof. It is 320
pieces of evidence, and a warning that any explanation had better account for
all of them. The proof exists, and chapter 9 shows its shape by looking at what
happens when the conditions fail.

This is the theorem the subject rests on, and it is called **strong duality**.

Two problems, then. The one about plans is the **primal**; the one about prices
is the **dual**. Each is built from the other by turning it inside out. Rows
become variables, variables become rows, the objective and the stock levels
trade places, and the inequalities reverse. Do it twice and you are back where
you started, which is the sense in which neither one is the original.

> **In one sentence.** The best plan and the cheapest honest price list always
> agree exactly, which is what makes the second problem worth solving.

---

Chapter 5 of 10

Previous: [Every honest price list is a ceiling](../04-every-mix-is-a-ceiling/README.md)  
Next: [Which rules are actually holding you back](../06-who-is-binding/README.md)  
Contents: [lp-duality](../../README.md)
