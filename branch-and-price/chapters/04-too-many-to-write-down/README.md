<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · Too many to write down

The catch arrives immediately. The strong model needs one variable per pattern,
and patterns multiply.

A paper mill cutting a 5600mm roll into ten ordered widths has this many ways
to cut one roll:

![The number of patterns against the number of ordered widths, on a logarithmic
scale, climbing from tens to nearly four
trillion.](explosion.png)

**3,972,952,644,549 patterns.** One variable each. You cannot write that model
down, you cannot store it, and you certainly cannot hand it to a solver.

Almost all of those variables are worthless. A good answer uses a handful of
patterns and leaves the rest at zero. The difficulty is not the count. It is
that you cannot tell which handful matters until the thing is solved.

> **In one sentence.** The strong model is unwritable, and almost all of it is
> irrelevant, but you cannot tell which part until you have solved it.

---

Chapter 4 of 9

Previous: [One variable per pattern](../03-one-variable-per-pattern/README.md)  
Next: [Start with a few, and let the prices ask](../05-let-the-prices-ask/README.md)  
Contents: [branch-and-price](../../README.md)
