# Linear programming on a GPU

*The machine got wider, not faster.*

For thirty years the way to solve a linear program faster was a quicker
processor. What replaced it was a much wider one, and the simplex method cannot
use it — not for want of trying, but because of what simplex *is*.

Fourteen chapters on what a method would have to look like instead, starting from
the version that does not work.

**[Read it →](https://bayzhan8.github.io/Illuminate/lp-on-gpu/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/lp-on-gpu/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch0) | one term, and whether it settles |
| 1 | [How much arithmetic per byte](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch1) | 0.17 operations per byte |
| 2 | [The roofline](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch2) | 1.3% of the arithmetic, 14.5x the speed |
| 3 | [Why simplex is the wrong shape](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch3) | a chain of dependent decisions |
| 4 | [Reading the table two ways](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch4) | one table, read across and down |
| 5 | [Two players, one score](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch5) | the plan and the prices as opponents |
| 6 | [A method made of one operation](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch6) | two matrix products and a clamp |
| 7 | [The obvious version does not work](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch7) | the spiral that winds outward |
| 8 | [One term different](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch8) | anticipation, and the spiral reverses |
| 9 | [It turns fast and shrinks slowly](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch9) | it turns fast and closes in slowly |
| 10 | [Cancel the rotation](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch10) | averaging cancels the turn, for free |
| 11 | [Does it get the right answer?](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch11) | the same plan, and the same prices |
| 12 | [What it costs](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch12) | no legal plan until it converges, and no corner |
| 13 | [Where this leaves things](https://bayzhan8.github.io/Illuminate/lp-on-gpu/#ch13) | what actually changed |

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
