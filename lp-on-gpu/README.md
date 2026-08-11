# Linear programming on a GPU

*The machine got wider, not faster.*

For thirty years the way to solve a linear program faster was a quicker
processor. What replaced it was a much wider one, and the simplex method cannot
use it — not for want of trying, but because of what simplex *is*.

Eleven chapters on what a method would have to look like instead, starting from
the version that does not work.

**[Read it →](https://bayzhan8.github.io/Illuminate/lp-on-gpu/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/lp-on-gpu/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](chapters/00-what-this-is/) | two methods, one term apart |
| 1 | [Wider, not faster](chapters/01-wider-not-faster/) | 0.17 operations per byte |
| 2 | [The wrong shape](chapters/02-the-wrong-shape/) | why simplex is a chain |
| 3 | [One operation](chapters/03-one-operation/) | a method built from matrix products |
| 4 | [The obvious version](chapters/04-the-obvious-version/) | spirals outward, cycles forever |
| 5 | [One term different](chapters/05-one-term-different/) | and it spirals inward |
| 6 | [Fast turn, slow shrink](chapters/06-fast-turn-slow-shrink/) | 11.5° a step, 2% closer |
| 7 | [Cancel the rotation](chapters/07-cancel-the-rotation/) | restarts, worth 10⁶ for free |
| 8 | [The same answer](chapters/08-the-same-answer/) | checked against the exact solver |
| 9 | [What it costs](chapters/09-what-it-costs/) | no legal plan, no corner |
| 10 | [Where this leaves things](chapters/10-where-this-leaves-things/) | honestly |

## The claim

There is no GPU in this repository and none is needed. Everything here is about
the *shape* of the iteration, which is what decides whether a wide machine can
be used, and that is as visible at three variables as at three million.

The method is checked against the exact rational simplex from
[lp-duality](../lp-duality/), which shares no line of code with it. It finds the
same plan and the same shadow prices to fifteen decimal places — the prices for
free, since they are half of what the method is.

The guide deliberately quotes **no benchmark figures and names no products**. A
test enforces that. This area moves quickly and a guide that dates in six
months is worse than one that does not try; the primary sources are named at
the end instead.

```bash
cd .. && make bootstrap
cd lp-on-gpu && make check
```
