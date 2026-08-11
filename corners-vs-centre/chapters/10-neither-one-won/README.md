<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · Neither one won

![Two side-by-side plots of the same corner at scales differing by a hundred.
In each, a red curve approaches from below and stops just short of the corner
with a blue arrow bridging the remaining distance. The two pictures are
indistinguishable.](crossover.png)

Both panels show the same corner. The right one is drawn a hundred times
larger, with the repulsion turned down a hundredfold, and the point lands
exactly 100 times closer. The picture does not change. Zooming in and
tightening the tolerance move together, so **there is no setting at which the
point becomes a corner**. It never lands.

Often that does not matter. Sometimes it matters a great deal:

- Reading off *which rules are binding*, which is what a shadow price is
  attached to, needs an actual corner. Nearly-tight is not tight.
- Warm starting. Change one number in the model and a simplex basis usually
  re-optimises in a few pivots. An interior point solve mostly starts again,
  which is why branch-and-bound trees, where thousands of nearly-identical LPs
  are solved in sequence, still run on simplex.
- Anything downstream that wants a vertex, including most of what
  [branch and price](../branch-and-price/) does.

So a modern barrier solve usually ends with **crossover**: hand the interior
point to a simplex-style routine and let it walk the short distance to a real
corner. The two methods are not competitors in the same program. They are
stages of it.

The rough division of labour today:

| | tends to win on |
|---|---|
| **simplex** | small and medium models, warm starts, anything inside a search tree, when you need a basis |
| **interior point** | very large and sparse models, first solves from cold, when you want a forecastable stopping point |
| **crossover** | whenever the second one is faster but the answer has to be a corner |

And the theoretical question underneath all of it is still open. Nobody knows
whether a pivot rule exists that makes simplex polynomial. Nobody knows whether
a *strongly* polynomial algorithm for linear programming exists at all: one
whose step count depends only on the number of rules and variables, not on how
many digits the numbers have. That is the ninth of Smale's problems for the
21st century, and it is unsolved.

Two methods, seventy-odd years, and the argument is not finished.

> **In one sentence.** The walk and the path solve different halves of the same
> job, which is why every serious solver contains both and finishes with the
> first one.

---

Chapter 10 of 10

Previous: [A gap you can forecast](../09-a-gap-you-can-forecast/README.md)  
Contents: [corners-vs-centre](../../README.md)
