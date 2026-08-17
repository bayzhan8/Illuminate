<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 0 · What this is

![Two curves against iteration count on the same workshop. One oscillates
violently between zero and eight hundred without ever settling. The other rises
smoothly and stops on three hundred and fifty.](hero.gif)

Each curve is what one method believes its current plan is worth, plotted
against how many rounds of arithmetic it has done. The problem behind them is a
workshop with three shelves of raw material and two things it can build, small
enough that the right answer is known exactly and is $350.

The blue one climbs and stops on $350.

The red one never settles. Four thousand rounds in it is still swinging between
$0 and $753, and it will keep swinging forever.

Now the part that makes this worth a guide. Neither curve is a bug, and neither
method is badly tuned. They were given the same problem, the same starting
point and the same step sizes, and their two update rules are identical except
for a single extra term in one line. That one term is the difference between a
method that works and a method that does not exist.

Both of these methods are built the way they are for one reason: their inner
loop is nothing but multiplying a table of numbers by a list of numbers, over
and over. That is the one kind of work a graphics processor can do thousands of
ways at once, and it is the reason anybody tolerates a method this fragile. The
guide is the case for that trade — what the hardware demands, what a method
shaped to satisfy it looks like, what the missing term is, and what you give up
by taking the deal.

> **In one sentence.** There is a method that can use parallel hardware, but
> only just, and what separates it from a method that never converges is one
> term in one line.

---

Chapter 0 of 13

Next: [How much arithmetic per byte](../01-arithmetic-per-byte/README.md)  
Contents: [lp-on-gpu](../../README.md)
