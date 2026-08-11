<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · Start with a few, and let the prices ask for more

Start with a model that is obviously too small. Take a few patterns — say the
lazy ones, each board cut into copies of a single length — and solve *that*.
This is the **restricted master**: the real model, restricted to the columns
you have bothered to write down.

For our order, starting with three lazy patterns, it says: **7 boards.**

That is an honest upper bound (those patterns really do fill the order) but it
is not the answer to the strong model, because the strong model has three more
patterns we have not written down. The question is whether any of them would
help — and answering it without adding them is exactly the trick.

Solve the restricted master and read off its **prices**, one per ordered
length. From the duality guide: these are what one more piece of that length
would be worth. At the first round they come out as

| length | price |
|---|---|
| 4 ft | 1/6 |
| 9 ft | 1/2 |
| 10 ft | 1/2 |

Now take *any* pattern, written down or not. Cutting a board with it costs one
board. The pieces that come off it are worth, at these prices, some amount. So
the pattern is worth adding exactly when

> the pieces it yields are worth **more than one board.**

That comparison is the reduced cost, and it needs nothing but the prices. A
pattern you have never written down can be judged by it.

**This is the same statement as dual feasibility.** The prices from the
restricted master satisfy every dual constraint belonging to a pattern you have
got. If they satisfy the constraints of all the patterns you *have not* got
too, they are feasible for the full problem's dual, and the restricted answer
is the full answer — proved, without ever building the full model. A pattern
that violates its dual constraint is a missing column, and the two things are
the same thing seen from opposite sides.

---

← [Too many to write down](../04-too-many-to-write-down/README.md) · [all chapters](../..#chapters) · [Asking for a pattern is a knapsack](../06-a-knapsack/README.md) →
