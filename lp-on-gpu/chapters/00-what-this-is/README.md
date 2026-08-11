<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 0 · What this is

![Two curves against iteration count on the same workshop. One oscillates
violently between zero and eight hundred without ever settling. The other rises
smoothly and stops on three hundred and fifty.](hero.gif)

Each curve is what one method thinks its current plan is worth, plotted against
how many iterations it has run. The problem behind them is a workshop with
three shelves of raw material and two things it can build, and it is small
enough that the right answer is known exactly.

The red one never settles. It is still swinging between $0 and $753 after four
thousand iterations, and it will do that forever.

The blue one stops on $350, which happens to be exactly right.

Neither is a bug, and neither is badly tuned. The two updates differ by one
term in one line, and most of this guide is about that term: where it comes
from, why anyone would want a method built this way, and what it still cannot
do.

> **In one sentence.** A method that can use parallel hardware is available,
> but only just, and the difference between it working and not is very small.

---

Chapter 0 of 13

Next: [How much arithmetic per byte](../01-arithmetic-per-byte/README.md)  
Contents: [lp-on-gpu](../../README.md)
