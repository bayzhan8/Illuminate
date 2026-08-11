<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · The obvious model, and why it is too weak

The natural way to model this is to decide, for each board, what comes off it:
take a pile of boards, mark some of them "used", and assign pieces to them
without overfilling any.

Relax that, letting a board be 30% used and a piece be split across two boards,
and the answer it gives is:

> total length ordered ÷ board length
> = (3×4 + 6×9 + 7×10) ÷ 25 = 136 ÷ 25 = **5.44 boards**

Why that particular ratio? Because once a piece may be sawn anywhere and its
two halves counted against two different boards, nothing can be stranded. A
board with 6 feet spare no longer wastes them: the next piece simply starts
there and finishes on the board after. Every constraint about fitting has
dissolved, and the only thing the model still has to respect is material. The
order asks for 136 feet of wood. Each board supplies 25 feet of it, none of
which need go to waste. So fewer than 136 ÷ 25 boards cannot supply the wood,
and 136 ÷ 25 boards can. The bound is the ratio because the relaxation removed
every other obstacle.

It is a genuine lower bound and it is useless, for the reason just given: this
is the answer you would get if boards were *liquid*, and the leftover at the
end of one board carries over to the next. Round it up and six boards might do.

Six boards will not do. The relaxation cannot see it, because the fact that
makes it impossible — a 10-foot piece sits on one board, whole — is precisely
what was relaxed away.

> **In one sentence.** Relaxing the obvious model throws away the very thing
> that makes the problem hard, so its bound is far too low.

---

Chapter 2 of 9

Previous: [The order](../01-the-order/README.md)  
Next: [One variable per pattern](../03-one-variable-per-pattern/README.md)  
Contents: [branch-and-price](../../README.md)
