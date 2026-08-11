<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · The obvious model, and why it is too weak

The natural way to model this is to decide, for each board, what comes off it:
take a pile of boards, mark some of them "used", and assign pieces to them
without overfilling any.

Relax that, letting a board be 30% used and a piece be split across two boards,
and the answer it gives is:

> total length ordered ÷ board length
> = (3×4 + 6×9 + 7×10) ÷ 25 = 136 ÷ 25 = **5.44 boards**

That is a genuine lower bound and it is useless, because of what the relaxation
quietly permits: the leftover at the end of one board carries over to the next.
It is the answer you would get if boards were *liquid*. Round it up and six
boards might do.

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
