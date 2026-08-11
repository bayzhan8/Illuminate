<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · A method made of one operation

So ask for the opposite. What would a method look like if the *only* thing it
ever did was multiply by the matrix?

Here is the setup. The workshop from the duality guide: three shelves, two
products, and the question of what to build. Written for a machine, it is

> choose a plan `x`, at least zero in every entry,
> so that `Ax` stays under the shelf limits `b`,
> making the profit as large as possible.

The duality guide's second idea gives the other half. Attach a price to each
shelf, collect them in `y`, and consider

> `L(x, y)` = what the plan costs, plus the prices times how much the plan
> overruns each shelf.

The plan wants this small. The prices want it large: if a shelf is overrun,
raising its price punishes the plan for it. The answer is the standstill where
neither side can improve by moving: the plan is the best one, and the prices
are the shadow prices of chapter 7 over there.

Now the point. To move the plan you need `A` transposed times `y`. To move the
prices you need `A` times `x`. And then you clamp anything that went negative
back to zero.

That is the whole vocabulary. Two matrix-vector products, some vector
addition, and a clamp. **No factorisation, no basis, no pivoting, no ordering,
nothing sequential.**

It is exactly the shape chapter 1 asked for. The only question left is whether
it works.

> **In one sentence.** Treating the plan and the prices as two players lets you
> build a method out of nothing but matrix-vector products.

---

Chapter 3 of 10

Previous: [Why simplex is the wrong shape](../02-the-wrong-shape/README.md)  
Next: [The obvious version does not work](../04-the-obvious-version/README.md)  
Contents: [lp-on-gpu](../../README.md)
