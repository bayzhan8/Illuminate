<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 9 · Where this leads

The shape of what just happened is more general than cutting boards.

**Dantzig–Wolfe decomposition** is the name for what chapter 3 did. A problem
with block structure is rewritten so its variables are *whole feasible
solutions of one block* rather than the block's individual variables. Here the
block is "one board" and its feasible solutions are the patterns. The new
relaxation sits between the integer hull and the naive relaxation, which is the
general reason it is tighter and why anyone tolerates the extra machinery.

Column generation is how you optimise over those solutions without listing
them. The pricing problem generates them on demand, producing precisely the
extreme points of the block that the current prices ask for.

**Benders decomposition** points the same idea the other way. It generates
*rows* rather than columns: fix the hard decisions, solve what is left, and
take the dual of that leftover problem as a new constraint to send back. Every
Benders cut is a price list doing exactly the job it did in chapter 5, proving
a proposal cannot be as good as it claims.

### When pricing is just filtering a list

A case that resembles the above and is not.

Suppose the columns are not defined by a polyhedron but *pre-generated*: a fixed
list of candidate driver schedules, say, computed in advance. Then there is no
optimisation problem to solve for the best column. You scan the list and take
the best reduced cost. The algorithm still works and the surrounding
branch-and-price machinery is unchanged.

But it is no longer generating the extreme points of a block. It is
reduced-cost filtering of a discretised approximation of one, and the bound you
get is a bound for *that* approximation. If a schedule you needed is absent
from the list, nothing in the method will ever say so. Whatever produced the
list made a modelling decision on your behalf.

## What the plain words are really called

| this guide says | everyone else says |
|---|---|
| a pattern | a column |
| the model with one variable per pattern | the **Dantzig–Wolfe** reformulation / master problem |
| the model with the patterns you bothered to write down | the **restricted master problem** |
| a price for each ordered length | a dual variable |
| worth more than one board | negative **reduced cost** |
| asking for a pattern | the **pricing problem** / subproblem |
| the loop | **column generation** |
| the loop inside a search tree | **branch-and-price** |
| the obvious model, relaxed | the natural LP relaxation |
| generating rows instead of columns | **Benders decomposition** |

## Further reading

The cutting-stock treatment here follows the spirit of chapters 2.2 and 8 of
*Integer Programming* by Conforti, Cornuéjols and Zambelli, which is the place
to go next and does properly what this page does with pictures.

## Running the code

```bash
make venv     # once, from the repository root
make test     # re-check every number this page quotes
make figures  # re-render every image
```

The solver reuses the exact-fraction simplex from
[the duality topic](../lp-duality/) rather than carrying a second copy. This
topic really is that one under load. The tests check the mathematics, the prose
against the code, and branch-and-price against a brute-force solver that
enumerates every pattern.

---

Chapter 9 of 9

Previous: [Branching, when the answer is 6.5 boards](../08-branch-and-price/README.md)  
Contents: [branch-and-price](../../README.md)
