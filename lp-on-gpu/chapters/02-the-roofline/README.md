<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · The roofline

Put 0.17 against the machines and the picture resolves.

![A log-log chart of achievable rate against arithmetic intensity, with a
ceiling line for each of two machines. At the intensity of a sparse
matrix-vector product, one machine reaches nine percent of its arithmetic and
the other one point three percent, while their absolute rates differ by the
ratio of their bandwidths.](roofline.png)

A machine has an intensity of its own, and it is the break-even point: divide
its arithmetic rate by its bandwidth and you get the number of operations it can
perform in the time it takes to deliver one byte. Feed it work above that
number and its memory system keeps up and the arithmetic runs flat out. Feed it
work below, and the arithmetic waits.

That is what the chart draws. Each machine's ceiling rises with intensity until
it hits the flat roof of its own arithmetic, and the two regimes meet at that
break-even point.

The accelerator can perform **13 operations for every byte** it delivers. Give
it work that asks for 0.17 and almost all of that arithmetic sits idle: it
reaches **1.3%** of what it could do, because 0.17 divided by 13 is about a
hundredth. The server processor, which can perform 1.9 operations per byte,
reaches **9%** of its own, by the same division. Our work sits far to the left
of both roofs.

Now the consequence, which is the reason this chapter exists. The accelerator
is still the faster machine here, by **14.5×** — and 14.5 is precisely the
ratio of their *bandwidths*, not the ratio of their arithmetic, which is about
a hundred. Both machines are being starved. The one with the fatter pipe is
starved less, and by exactly the ratio of the pipes.

So for this kind of work, buying a machine with more arithmetic buys you
nothing. Buying one with more bandwidth buys you exactly what it says on the
label, no more and no less.

Which tells you what a good algorithm looks like on hardware like this: one
whose entire inner loop is streaming over the matrix, and which does no other
kind of work at all.

> **In one sentence.** Sparse matrix work is limited by memory bandwidth, not
> arithmetic, so the only speedup a wider machine can offer is its bandwidth
> ratio.

---

Chapter 2 of 13

Previous: [How much arithmetic per byte](../01-arithmetic-per-byte/README.md)  
Next: [Why simplex is the wrong shape](../03-the-wrong-shape/README.md)  
Contents: [lp-on-gpu](../../README.md)
