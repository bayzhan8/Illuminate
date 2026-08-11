<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · Wider, not faster

Start with the hardware, because it determines which algorithms are worth
having.

A modern accelerator has enormously more arithmetic capability than a server
processor. It does not have proportionally more memory bandwidth. Roughly: a
hundred times the arithmetic, but only about fifteen times the rate at which it
can fetch numbers to do arithmetic *on*.

That matters only if you know how much arithmetic your work does per byte it
reads. So count it.

Multiplying a sparse matrix by a vector, the way solvers store matrices, costs
about **12 bytes per stored entry**: eight for the value and four to record
which column it sits in. And it performs **2 operations**: one multiply, one
add.

Two operations per twelve bytes. **0.17 operations per byte.**

Now put that against the machines.

![A log-log chart of achievable rate against arithmetic intensity, with a
ceiling line for each of two machines. At the intensity of a sparse
matrix-vector product, one machine reaches nine percent of its arithmetic and
the other one point three percent, while their absolute rates differ by the
ratio of their bandwidths.](roofline.png)

The accelerator can perform **13 operations for every byte** it delivers. Give
it work that asks for 0.17 and almost all of that arithmetic sits idle: it
reaches **1.3%** of what it could do. The server processor, which can perform
1.9 operations per byte, reaches **9%** of its own.

And yet the accelerator is still the faster machine here, by **14.5×**, which
is precisely the ratio of their *bandwidths*, not the ratio of their
arithmetic, which is about a hundred.

That is the sentence to carry forward. For this kind of work, buying a machine
with more arithmetic buys you nothing. Buying one with more bandwidth buys you
exactly what it says.

Which tells you what a good algorithm looks like: one whose entire inner loop
is streaming over the matrix, and which does no other kind of work at all.

> **In one sentence.** Sparse matrix work is limited by memory bandwidth, not
> arithmetic, so the only speedup available is the bandwidth ratio.

---

Chapter 1 of 10

Previous: [What this is](../00-what-this-is/README.md)  
Next: [Why simplex is the wrong shape](../02-the-wrong-shape/README.md)  
Contents: [lp-on-gpu](../../README.md)
