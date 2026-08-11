<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · Wider, not faster

Start with the hardware, because it determines which algorithms are worth
having.

A modern accelerator has enormously more arithmetic capability than a server
processor. It does not have proportionally more memory bandwidth. Roughly: a
hundred times the arithmetic, but only about fifteen times the rate at which it
can fetch numbers to do arithmetic *on*.

Which of those two numbers you get depends on your work, and there is a single
question that decides it. **How much arithmetic do you get to do for every byte
you had to fetch to do it?** Multiply two dense matrices and the answer is
enormous: every number you load is used hundreds of times over. Add two long
lists of numbers and the answer is dismal: load sixteen bytes, do one addition,
move on. Everyone calls this ratio *arithmetic intensity*, and it is the only
property of a computation the next chart cares about.

So count it for the operation this guide is about. Multiplying a sparse matrix
by a vector, the way solvers store matrices, costs about **12 bytes per stored
entry**: eight for the value and four to record which column it sits in. Having
fetched that entry, you do **2 operations** with it: one multiply, one add. Then
you never look at it again.

Two operations per twelve bytes. **0.17 operations per byte.** About as poor
as it gets.

Now put that against the machines.

![A log-log chart of achievable rate against arithmetic intensity, with a
ceiling line for each of two machines. At the intensity of a sparse
matrix-vector product, one machine reaches nine percent of its arithmetic and
the other one point three percent, while their absolute rates differ by the
ratio of their bandwidths.](roofline.png)

A machine has an intensity of its own: divide its arithmetic rate by its
bandwidth and you get the number of operations it can perform in the time it
takes to deliver one byte. Below that number the arithmetic is starved; above
it, fed. Feed it work above that number and its memory system keeps up and the
arithmetic runs flat out. Feed it work below, and the arithmetic waits.

The accelerator can perform **13 operations for every byte** it delivers. Give
it work that asks for 0.17 and almost all of that arithmetic sits idle: it
reaches **1.3%** of what it could do, because 0.17 divided by 13 is about a
hundredth. The server processor, which can perform 1.9 operations per byte,
reaches **9%** of its own, by the same division. The chart says only this much: each machine's ceiling rises with intensity until it hits the flat
roof of its own arithmetic, and our work sits far to the left of both roofs.

And yet the accelerator is still the faster machine here, by **14.5×**, which
is precisely the ratio of their *bandwidths*, not the ratio of their
arithmetic, which is about a hundred. Both machines are being starved; the one
with the fatter pipe is starved less.

For this kind of work, buying a machine with more arithmetic buys you nothing.
Buying one with more bandwidth buys you exactly what it says.

Which tells you what a good algorithm looks like: one whose entire inner loop
is streaming over the matrix, and which does no other kind of work at all.

> **In one sentence.** Sparse matrix work is limited by memory bandwidth, not
> arithmetic, so the only speedup available is the bandwidth ratio.

---

Chapter 1 of 10

Previous: [What this is](../00-what-this-is/README.md)  
Next: [Why simplex is the wrong shape](../02-the-wrong-shape/README.md)  
Contents: [lp-on-gpu](../../README.md)
