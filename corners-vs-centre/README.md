# Simplex against interior point

*Along the edge, or through the middle.*

Two serious methods for linear programming, invented thirty-seven years apart.
One walks the boundary corner to corner and never steps inside. The other
starts in the middle and follows a curve that approaches the answer without
ever reaching it.

Fifteen chapters on why there are two, which is mostly a question about a proof
from 1972 and what it does and does not say.

**[Read it →](https://bayzhan8.github.io/Illuminate/corners-vs-centre/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/corners-vs-centre/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](chapters/00-what-this-is/) | two routes, one answer |
| 1 | [A new kind of problem](chapters/01-a-new-kind-of-problem/) | where the region and the question came from |
| 2 | [Along the edge](chapters/02-along-the-edge/) | the walk, and why it may stop |
| 3 | [It should have been slow](chapters/03-it-should-have-been-slow/) | the corner count says it cannot work |
| 4 | [Klee and Minty build a cube](chapters/04-the-cube/) | the cube that visits every corner |
| 5 | [The rule, not the method](chapters/05-not-the-rule/) | change one function, lose the exponent |
| 6 | [Not cycling is not the same as being fast](chapters/06-not-cycling-is-not-fast/) | a guarantee to finish is not a guarantee to be quick |
| 7 | [Every rule has a cube](chapters/07-every-rule-has-a-cube/) | every rule has a cube of its own |
| 8 | [Why nobody ever meets one](chapters/08-why-nobody-meets-one/) | the bad cases are knife-edges |
| 9 | [Polynomial, and slower](chapters/09-polynomial-and-slower/) | polynomial, and slower than the walk |
| 10 | [The wall that pushes back](chapters/10-the-wall-that-pushes-back/) | a penalty with no floor |
| 11 | [The central path](chapters/11-the-central-path/) | the curve of exact answers to wrong questions |
| 12 | [What the barrier actually does](chapters/12-what-the-barrier-does/) | one bowl, and Newton's method on it |
| 13 | [A gap you can forecast](chapters/13-a-gap-you-can-forecast/) | the receipt a path point carries |
| 14 | [Neither one won](chapters/14-neither-one-won/) | crossover, and the division of labour |

## The claim chapters 5 and 6 rest on

The Klee-Minty cube is usually presented as a fact about the simplex method.
It is a fact about a *pivot rule*, and the difference is checkable rather than
arguable. The same code on the same cubes, with one function substituted:

| rule | pivots on the n-cube | at n = 10 |
|---|---|---|
| Dantzig | exactly 2ⁿ − 1 | 1023 of 1024 corners |
| Bland | exactly 2·Fib(n+1) − 1 | 177 |
| steepest edge | 1 | 1 |

Bland's rule is the interesting row. Its guarantee is that it cannot cycle, and
it is easy to read that as a guarantee of speed. The counts say otherwise: 3, 5,
9, 15, 25, 41, 67, 109, 177, a sequence whose ratio settles on the golden ratio.
Still exponential, with a smaller base. The tests assert both closed forms
against the formulas at every dimension up to 12, not against stored numbers.

## How the numbers are checked

The simplex here is exact rational arithmetic with a pluggable pivot rule, so a
step count is a step count rather than an artefact of rounding near a degenerate
corner. Everything else is checked against something that shares no code with
it:

- the walk against brute-force enumeration of every corner in the workshop
- the barrier and the ellipsoid against the exact optimum the simplex returns
- the JavaScript running the two sandbox pages against the Python, over the
  same inputs, in the test suite

The barrier's own guarantee is checked as a guarantee: at every μ tested, the
real gap sits under the promised 5μ.

## Running it

```bash
make bootstrap    # once, from the repository root
cd corners-vs-centre
make render       # regenerate every figure
make publish      # regenerate chapters/, index.html, sandbox/
make verify       # re-check every number in lesson.md
```
