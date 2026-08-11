<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · Start with a few, and let the prices ask for more

Start with a model that is obviously too small.

Take a few patterns — say the lazy ones, each board cut into copies of a single
length — and solve *that*. This is the **restricted master**: the real model,
restricted to the columns someone has bothered to write down.

For our order, starting with three lazy patterns, it says: 7 boards. That is an
answer to a smaller question than the one we asked.

That is an honest upper bound, since those patterns really do fill the order.
It is not the answer to the strong model, which has three more patterns nobody
has written down. Whether any of them would help, answered without adding them,
is the whole method.

Solve the restricted master and read off its **prices**, one per ordered
length. From the duality guide: these are what one more piece of that length
would be worth. At the first round they come out as

| length | price |
|---|---|
| 4 ft | 1/6 |
| 9 ft | 1/2 |
| 10 ft | 1/2 |

Now take *any* pattern, written down or not.

Cutting a board with it costs one board. The pieces that come off it are worth,
at these prices, some amount. So the pattern is worth adding exactly when

> the pieces it yields are worth **more than one board.**

That comparison is the reduced cost. It needs nothing but the prices, so a
pattern nobody has written down can still be judged by it.

**This is the same statement as dual feasibility.** The prices from the
restricted master satisfy every dual constraint belonging to a pattern you have
got. If they satisfy the constraints of all the patterns you *have not* got
too, they are feasible for the full problem's dual, and the restricted answer
is the full answer, proved without ever building the full model. A pattern that
violates its dual constraint is a missing column. The two statements are one
statement seen from opposite sides.

> **In one sentence.** The prices from a small model can judge a pattern that
> model has never seen, which turns "is anything missing" into arithmetic.

---

Chapter 5 of 9

Previous: [Too many to write down](../04-too-many-to-write-down/README.md)  
Next: [Asking for a pattern is a knapsack](../06-a-knapsack/README.md)  
Contents: [branch-and-price](../../README.md)
