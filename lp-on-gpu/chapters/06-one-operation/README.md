<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · A method made of one operation

Now the payoff, and it is why the last two chapters were worth the trouble.

To improve the plan you need to know, at the current prices, whether a product
earns more than its ingredients cost. That comparison is the profit against
`Aᵀy`.

To improve the prices you need to know which shelves are overdrawn. That is
`Ax` against `b`.

Two questions, two readings of the same table, one matrix-vector product each.
Then you clamp anything that went negative back to zero, because there are no
negative chairs and no negative prices.

That is the entire vocabulary of the method. Two matrix-vector products, some
vector addition, and a clamp. **No factorisation, no basis, no pivoting, no
ordering, nothing sequential.**

Look back at what chapter 3 said simplex could not avoid — a chain of dependent
decisions and a triangular solve — and then at what chapter 2 said the hardware
wants: an inner loop that does nothing but stream over the matrix. This is that
loop and nothing else.

The only question left is whether it works.

> **In one sentence.** Letting the plan and the prices take turns gives a method
> whose whole inner loop is two passes over the matrix.

---

Chapter 6 of 13

Previous: [Two players, one score](../05-two-players/README.md)  
Next: [The obvious version does not work](../07-the-obvious-version/README.md)  
Contents: [lp-on-gpu](../../README.md)
