<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 11 · Where this leads

Everything above is one small problem solved by hand. What makes duality worth
this much attention is what gets built on it.

- **The simplex method** decides which product to bring into a plan by asking
  whether its dual row is violated. The "reduced cost" in any solver's log is
  the amount by which a product's ingredients cost less than it earns.
- **Column generation** turns that around. When there are too many possible
  products to write down, solve with a few, read the prices off the dual, and
  use those prices to *ask* whether some product you have not written down yet
  would be worth adding. The prices are the entire interface between the two
  halves.
- **Dantzig–Wolfe decomposition** is that idea applied to a problem with
  repeated structure, and **branch and price** is what you get when the pieces
  have to come out whole.
- **Benders decomposition** cuts the other way: fix the hard decisions, solve
  what is left, and take the *dual* of that leftover problem as a new rule to
  send back. Every Benders cut is a price list from chapter 3, doing the job it
  did there: proving a proposal cannot be as good as it claims.

The next guide, [along the edge, or through the middle](../corners-vs-centre/),
takes the first of those apart: how the walk uses the dual row to choose, and
what a rival method that refuses corners does instead. [Solving a model you
never wrote down](../branch-and-price/) is the second of them under load.

---

Chapter 11 of 11

Previous: [A plan that cannot exist](../10-no-such-plan/README.md)  
Contents: [lp-duality](../../README.md)
