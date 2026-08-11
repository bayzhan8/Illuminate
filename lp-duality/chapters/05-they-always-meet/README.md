<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · They always meet

So plans push up from below and price lists press down from above. The question
is whether they meet, or whether they stop with a gap between them that nothing
can close.

![Real plans appearing along a dollar scale from the left, and real price lists
appearing from the right, with the band of remaining possibilities shrinking
until it is a single point at three hundred and fifty
dollars.](meet.gif)

They meet. The best plan earns **$350** and the cheapest honest price list
charges **$350**, and the space in between has nothing left in it.

It would be fair to suspect this workshop of being rigged. So here are 320 more
workshops, invented at random — different numbers of products, different
numbers of shelves, different recipes — each one solved twice from scratch, once
for its best plan and once, as a completely separate problem, for its cheapest
prices.

![A scatter plot of the best plan's profit against the cheapest price list's
bill for three hundred and twenty random workshops. Every point lies on the
diagonal.](always.png)

Every point is on the diagonal, and because both sides are computed in exact
fractions the largest disagreement across all 320 is not "small" — it is zero.

This is the theorem that makes the subject work. It has a name — **strong
duality** — and it is worth being clear about what the picture above is and is
not. It is not a proof. It is 320 pieces of evidence and a warning that any
proposed explanation had better predict all of them. The proof exists, and
chapter 9 shows the shape of it by looking at what happens when the theorem's
conditions fail.

Two problems, then. The one about plans is called the **primal**; the one about
prices is called the **dual**. Each is built from the other by turning it inside
out — rows become variables, variables become rows, the objective and the stock
levels trade places, and the inequalities reverse. Do it twice and you are back
where you started, which is the sense in which neither one is the original.

---

Chapter 5 of 10

Previous: [Every honest price list is a ceiling](../04-every-mix-is-a-ceiling/README.md)  
Next: [Which rules are actually holding you back](../06-who-is-binding/README.md)  
Contents: [lp-duality](../../README.md)
