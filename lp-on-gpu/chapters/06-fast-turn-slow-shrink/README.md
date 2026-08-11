<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · It turns fast and shrinks slowly

The spiral converges. The trouble is how.

On the small problem the iteration is exactly a linear map, so it can be taken
apart completely. Its eigenvalues are a conjugate pair, and a conjugate pair
means the step is a rotation combined with a shrink. Both have closed forms.
With a step size of 0.2:

- it turns **11.5°** per iteration, so a full revolution takes **31.2** steps
- it shrinks the distance to the answer by **2.0%** per iteration

Those two numbers are the whole difficulty. It is spinning quickly and closing
in barely at all.

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
