<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · It turns fast and shrinks slowly

The spiral converges. The trouble is how.

Look at what one step of the inward spiral does. It carries the point some way
*around* the answer, and it brings it a little way *in*. A turn and a shrink,
over and over, and not only in the drawing. On the toy problem there is no clamping and no case analysis, so if you measure the state
as an offset from the answer, one iteration is exactly "multiply that offset by
a fixed two-by-two matrix", and it is the same matrix every time.

A matrix that turns everything has no direction it merely stretches, so it has
no real eigenvalues. What it has instead is a conjugate pair of complex ones,
and a complex number carries exactly two pieces of information, which here are
the two things the spiral is doing: the angle of the pair is how far one step
turns, and the size of the pair is what one step multiplies the distance by.
Both come out in closed form. With a step size of 0.2:

- it turns **11.5°** per iteration, so a full revolution takes **31.2** steps
- it shrinks the distance to the answer by **2.0%** per iteration

Put them together and the difficulty is plain. Thirty-one steps of shaving 2%
off a distance leave you about half as far away as you began, so one full
revolution of that spiral buys you one halving. It is spinning quickly and
closing in barely at all.

And you cannot fix it by taking bigger steps, because the two are locked
together.

![Two curves against step size on shared axes: degrees turned per iteration
rising steeply, and percent closer per iteration rising with
it.](anatomy.png)

Raising the step size does make it contract faster. It also makes it rotate
faster, and past a threshold the method stops converging at all. The setting
that keeps it stable is the setting that makes it crawl.

So most of the work is going into going round, and only a sliver into going in.

> **In one sentence.** The iteration rotates far more than it contracts, and
> the step size cannot fix that because it drives both.

---

Chapter 6 of 10

Previous: [One term different](../05-one-term-different/README.md)  
Next: [Cancel the rotation](../07-cancel-the-rotation/README.md)  
Contents: [lp-on-gpu](../../README.md)
