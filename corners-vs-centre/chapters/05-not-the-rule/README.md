<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · The rule, not the method

![A logarithmic chart of pivot counts against cube dimension. One straight line
doubles with each dimension. A second straight line climbs more gently. A third
is flat at one pivot for every size.](by-rule.png)

The cube proves less than it looks as though it proves.

The three lines above come from the same simplex code on the same cubes. One
function differs: which improving column to enter. That single substitution
moves the count from doubling, to a gentler climb, to a single pivot.

- **Dantzig's rule** takes exactly **2ⁿ − 1** pivots. Every corner.
- **Bland's rule**, which takes the lowest-numbered improving column, takes
  exactly **2·Fib(n+1) − 1**. At n = 10 that is 177 rather than 1023.
- **Steepest edge**, which measures improvement per unit of *movement* rather
  than per unit of variable, takes **one pivot**, at every size.

That middle formula needs unpacking, since it arrives out of nowhere. The
Fibonacci numbers are what you get by starting with 1 and 1 and making every
term the sum of the two before it: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, and on
up. Bland's count on the cube of dimension *n* is the term at position *n* + 1,
doubled, less one. At n = 10 the term is 89, so the count is 177.

Bland's rule deserves a moment, because it is easy to draw the wrong lesson
from it. Its guarantee is that it cannot cycle: it will always terminate. That
is a real and useful property, and it is why the other guides in this
repository use it. But look at the growth. 3, 5, 9, 15, 25, 41, 67, 109, 177.
Divide each of those by the one before it and watch the quotients. 5 over 3 is
one and two thirds; 9 over 5 is 1.8; 15 over 9 is back to one and two thirds.
They bounce about at first. Then they settle: by 109 over 67 they have almost
stopped moving, and 177 over 109 sits a whisker above 1.6 and is still edging
down. What they are closing in on is the golden ratio, about 1.618, which is
what ratios of consecutive Fibonacci numbers always do. So each extra dimension multiplies Bland's pivot count by
about 1.618, where Dantzig's rule multiplies by 2. It is still exponential,
just with a smaller base. Avis and Chvátal established this in 1978. **Not
cycling is not the same as being fast**, and the cube shows the difference
rather than merely asserting it.

Steepest edge escaping in one pivot is likewise not a proof of anything about
steepest edge. It means only that *this* cube was not built against *that*
rule. Deformed constructions have since been produced against essentially every
rule anyone has proposed, including randomised ones; Zadeh's rule held out
until 2022. **No pivot rule is known to be polynomial, and whether one exists
is open.**

The related geometric question is open too. The Hirsch conjecture asked whether
you always *could* get between two corners in few hops, whatever rule you used.
Klee and Walkup disposed of the unbounded case in 1967, and Francisco Santos
disproved the bounded version in 2012. The weaker polynomial Hirsch conjecture,
which asks only for a polynomial bound, remains unsettled.

Which leaves the question from chapter 3 wide open: bad cases exist for every
rule, so why does nobody meet one? The answer, from Daniel Spielman and
Shang-Hua Teng in 2004, is **smoothed analysis**. Take any input, including a
Klee-Minty cube, and jiggle it by a tiny random amount. The expected number of
pivots is then polynomial. The bad cases are real, but they are knife-edges:
perturb one and it stops being bad. Worst-case analysis had been asking a
question whose answer says very little about the inputs anybody actually has.

> **In one sentence.** The cube is an argument about a pivot rule, the bad
> cases survive for every rule anyone has tried, and they are nonetheless so
> fragile that a random nudge destroys them.

---

Chapter 5 of 10

Previous: [Klee and Minty build a cube](../04-the-cube/README.md)  
Next: [Polynomial, and slower](../06-polynomial-and-slower/README.md)  
Contents: [corners-vs-centre](../../README.md)
