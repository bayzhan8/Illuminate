<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · A decision made by arithmetic

Here is the best thing in this guide, and it happens in round 9.

Everything so far has deleted rows and columns — bookkeeping, however useful.
This is different. This is the loop settling one of the actual decisions in the
model, the kind a person would assume requires a search.

Product B needs 25 units in period 1. The balance row therefore forces
`makeB1 ≥ 25`. The link row says `makeB1 − 100 × openB1 ≤ 0`, so

> `openB1 ≥ makeB1 / 100 ≥ 25 / 100 = 0.25`

and `openB1` is a yes/no switch, so it is a whole number. The smallest whole
number at or above 0.25 is 1.

**The setup happens.** Not "probably happens", not "happens in the best
solution found so far". It is forced, it is proved, and it is proved by
division and rounding, before branch and bound has opened a single node.

That is four lines of arithmetic you can check by hand, and it disposes of a
binary decision permanently. A search would have had to try both branches and
prove one of them worthless.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/solvers/sandbox/04.html)**
Move demand and the big-M constant, and watch the switch stop being a decision.

Now the part that turns this into advice. Look at what the deduction leaned on:
the 100 in the link row, which is there only to mean "no limit, really". Make it
1,000,000 instead and the same chain gives `openB1 ≥ 0.000025`, which still
rounds to 1, so this particular deduction survives.

But look at what happens to the *fractional* relaxation of that row. At 100, a
model that wants to make 25 units must set `openB1` to at least 0.25 and pay a
quarter of the setup cost. At 1,000,000 it need only set it to 0.000025 and pays
essentially nothing, so the relaxation happily makes things in a factory it has
not paid to open. The bound it reports is correspondingly useless.

That is why "just use a big number" is the most expensive habit in integer
modelling. The constant does not change what is feasible. It changes how much
the relaxation is allowed to lie, and the relaxation is what prunes the tree.

> **In one sentence.** A loop of obvious steps can settle a yes/no decision by
> division and rounding, and how big you made your big-M decides how much that
> kind of reasoning is worth.

---

Chapter 4 of 14

Previous: [The cascade, and where the gap opens](../03-the-cascade/README.md)  
Next: [What it costs you](../05-what-it-costs/README.md)  
Contents: [solvers](../../README.md)
