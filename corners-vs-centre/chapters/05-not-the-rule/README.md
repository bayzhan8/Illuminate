<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · The rule, not the method

![A logarithmic chart of pivot counts against cube dimension. One straight line
doubles with each dimension. A second straight line climbs more gently. A third
is flat at one pivot for every size.](by-rule.png)

Chapter 4 reads like an indictment of the simplex method. It is not one. It is
an indictment of one line inside it.

The three lines above come from the same simplex code on the same cubes. One
function differs: the pivot rule, which picks the edge to walk along. That
single substitution moves the count from doubling, to a gentler climb, to a
single pivot.

- **Dantzig's rule** takes exactly **2ⁿ − 1** pivots. Every corner.
- **Bland's rule**, which ignores the numbers entirely and takes whichever
  improving edge comes first in a fixed ordering, takes exactly
  **2·Fib(n+1) − 1**. At n = 10 that is 177 rather than 1023.
- **Steepest edge**, which measures improvement per unit of *movement* rather
  than per unit of variable, takes **one pivot**, at every size.

Nothing else was touched. Same cube, same corners, same rule for deciding how
far to go once a direction is chosen, same stopping test. If the blow-up in
chapter 4 belonged to the walk, swapping a single function could not have moved
it, and it moved it from 1023 to 1.

So the honest reading of Klee and Minty is narrower than it first sounds. They
did not show that walking corners is exponential. They showed that *walking
corners while always taking the steepest immediate gain* is exponential, which
is a statement about greed.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/corners-vs-centre/sandbox/05.html)**
Hold the dimension steady and change only the rule, then hold the rule steady
and raise the dimension. One of those controls sets the exponent.

> **In one sentence.** The exponent in chapter 4 belongs to the rule that
> picked the edge, not to the method that did the walking.

---

Chapter 5 of 14

Previous: [Klee and Minty build a cube](../04-the-cube/README.md)  
Next: [Not cycling is not the same as being fast](../06-not-cycling-is-not-fast/README.md)  
Contents: [corners-vs-centre](../../README.md)
