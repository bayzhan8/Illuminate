<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · The obvious model, and why it is too weak

The natural way to model this is to decide, for each board, what comes off it:
take a pile of boards, mark some of them "used", and assign pieces to them
without overfilling any.

Relax that — let a board be 30% used, let a piece be split across two boards —
and the answer it gives is:

> total length ordered ÷ board length
> = (3×4 + 6×9 + 7×10) ÷ 25 = 136 ÷ 25 = **5.44 boards**

That is a real lower bound and it is useless, because of what the relaxation
quietly allows: it lets the leftover at the end of one board be carried over to
the next. It is the answer you would get if boards were *liquid*. Rounding it
up says six boards might do.

Six boards will not do. The relaxation cannot see that, because the thing that
makes it impossible — that a 10-foot piece has to sit on one board, whole — is
precisely what got relaxed away.

---

← [The order](../01-the-order/README.md) · [all chapters](../..#chapters) · [One variable per pattern](../03-one-variable-per-pattern/README.md) →
