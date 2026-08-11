<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · The cascade, and where the gap opens

Take those reductions one at a time and they are unremarkable. Run them in a
loop and something else happens.

![Two panels, each plotting how much of a model is left against how many rounds
of the reduction loop have run. Three stepped lines fall away in each: nonzeros,
columns and rows. Neither panel drops all at once; both keep stepping down for
many rounds.](cascade.png)

If presolve were a checklist applied once, those lines would fall in round one
and go flat. They do not. The small model takes **13 rounds** to settle and the
larger one takes **27**, because each reduction is what makes the next one
visible. Deleting a row creates a fixed column. Fixing a column empties a row.
Emptying a row narrows a bound. Narrowing a bound fixes another column.

Here is the best thing in this guide, and it happens in round 9.

Product B needs 25 units in period 1. The balance row therefore forces
`makeB1 ≥ 25`. The link row says `makeB1 − 100 × openB1 ≤ 0`, so

> `openB1 ≥ makeB1 / 100 ≥ 25 / 100 = 0.25`

and `openB1` is a yes/no switch, so it is a whole number. The smallest whole
number at or above 0.25 is 1.

**The setup happens.** Not "probably happens", not "happens in the best
solution found so far". It is forced, it is proved, and it is proved by
division and rounding, before branch and bound has opened a single node. One of
the actual decisions in the model has been made by arithmetic.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/solvers/sandbox/03.html)**
Move demand and the big-M constant, and watch the switch stop being a decision.

That is also the answer to why the big-M constant matters so much. Make it
1,000,000 instead of 100 and the same chain gives `openB1 ≥ 0.000025`, which
still rounds to 1, so this particular deduction survives. But every *fractional*
relaxation of that row gets weaker as the constant grows, which is why "just use
a big number" is the most expensive habit in integer modelling.

> **In one sentence.** The reductions feed each other, and the loop can settle
> a real decision without searching for it.

---

Chapter 3 of 10

Previous: [What presolve takes out](../02-what-it-removes/README.md)  
Next: [What it costs you](../04-what-it-costs/README.md)  
Contents: [solvers](../../README.md)
