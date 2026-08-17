<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · The obvious model, and why it is too weak

Chapter 0 gave two hand-made arguments about this order. This chapter and the
next are where they come from, and getting there needs two words.

To **model** a problem is to write it down as unknown quantities to be solved
for, together with the arithmetic those quantities must satisfy. To
**relax** a model is to then cross out one of those requirements on purpose,
producing an easier problem that a computer can solve quickly.

The point of doing that is not the easiness. Every arrangement that satisfied
the original requirements still satisfies the shortened list, so the relaxed
problem is choosing from a strictly larger set of candidates — and it may find
something in there that the real problem could not have used. Here the aim is to
use as few boards as possible, so a larger set of candidates can only bring the
answer *down*, never up. Whatever number the relaxation reports is therefore a
floor under the true one: the real answer cannot be below it. That is where a
lower limit comes from when nobody hands you a clever argument.

The requirement that gets crossed out is nearly always the same one:
**whole numbers**. Real answers here are whole boards and whole pieces, and
insisting on whole numbers is what makes a problem hard. Let the quantities go
fractional and the problem becomes easy. So every lower limit in this guide
comes from the same recipe: write the problem down, allow fractions, solve, and
read off the floor. The standard word for such a floor is a **bound**.

Now do that to the obvious model. The natural way to write cutting stock down
is to decide, for each board, what comes off it: take a pile of boards, mark
some of them "used", and assign pieces to them without overfilling any. The
unknowns are the marks and the assignments, and every one of them is a
whole-number yes-or-no.

Allow fractions, so that a board may be 30% used and a piece may be split
across two boards, and the answer it gives is:

> total length ordered ÷ board length
> = (3×4 + 6×9 + 7×10) ÷ 25 = 136 ÷ 25 = **5.44 boards**

which is chapter 0's first argument, arrived at mechanically rather than by
noticing anything.

Why does it land on exactly that ratio? Because once a piece may be sawn
anywhere and its two halves counted against two different boards, nothing can
be stranded. A board with 6 feet spare no longer wastes them: the next piece
simply starts there and finishes on the board after. Every requirement about
*fitting* has dissolved along with the whole numbers, and the only thing left
for the model to respect is material. The order asks for 136 feet of wood. Each
board supplies 25 feet of it, none of which need go to waste. So fewer than
136 ÷ 25 boards cannot supply the wood, and 136 ÷ 25 boards can. The bound is
the ratio because the relaxation removed every other obstacle.

It is a genuine lower limit, and it is useless, for the reason just given: this
is the answer you would get if boards were *liquid* and the leftover at the end
of one board flowed into the next. Round it up and six boards might do.

Six boards will not do. The relaxation cannot see it, because the fact that
makes it impossible — a 10-foot piece sits on one board, whole — is precisely
what was relaxed away.

> **In one sentence.** Relaxing the obvious model throws away the very thing
> that makes the problem hard, so its bound is far too low.

---

Chapter 2 of 11

Previous: [The order](../01-the-order/README.md)  
Next: [One variable per pattern](../03-one-variable-per-pattern/README.md)  
Contents: [branch-and-price](../../README.md)
