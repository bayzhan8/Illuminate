<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · Polynomial, and slower

![A sequence of increasingly elongated ellipses, each contained in the last,
tightening around a thin sliver of the workshop region near its best corner.](ellipsoids.gif)

In 1979 Leonid Khachiyan showed that linear programming is solvable in
polynomial time, using the ellipsoid method. This was genuine news. It made
newspapers outside mathematics, which is not a thing that happens to
algorithms.

The method ignores the region's shape completely. Wrap everything in an
ellipsoid and ask whether its centre is a legal plan. If it is not, then some
rule it breaks tells you the answer cannot be on that side, so throw that half
away and wrap the survivor in a new ellipsoid. Repeat. Each step shrinks the
volume by a guaranteed factor, so eventually the ellipsoid is smaller than any
region with room in it, and if you have not found a point by then there was
none.

The bound is honest and the method is dreadful. In two dimensions the
guaranteed shrink per step is exp(−1/4), about **0.779**: each cut is promised
to remove barely a fifth. This repository's implementation achieves **0.7698**
every single step, which is the smallest ellipsoid that can contain the
surviving half, and it never does better, because there is no mechanism by
which it could.

Ask it to find a plan worth at least $349 in the workshop and it takes **29
cuts**. The walk in chapter 2 reached the exact optimum of $350 in three hops.
Worse, the ellipsoid grinds at a fixed rate that follows directly from that
0.7698: shrinking a distance tenfold means shrinking an area a hundredfold,
which is **17.6 cuts per decimal digit**, forever. And it never produces an
exact answer at all.

That is the shape of the disappointment. Polynomial is a statement about how
the cost grows, not about how large it is, and a method can be polynomial and
still lose to an exponential one on every instance anybody runs. Khachiyan's
result reframed the theory of the subject and changed nobody's software.

> **In one sentence.** The first polynomial method took its worst case on every
> input, which is exactly why its worst case was provable.

---

Chapter 6 of 10

Previous: [The rule, not the method](../05-not-the-rule/README.md)  
Next: [Through the middle](../07-through-the-middle/README.md)  
Contents: [corners-vs-centre](../../README.md)
