<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · How much arithmetic per byte

Start with the hardware, because it determines which algorithms are worth
having.

A modern accelerator has enormously more arithmetic capability than a server
processor. It does not have proportionally more memory bandwidth. Roughly: a
hundred times the arithmetic, but only about fifteen times the rate at which it
can fetch numbers to do arithmetic *on*.

So a machine has two speeds, and which one you get is a property of your work
rather than of the machine. There is a single question that decides it.

> **How much arithmetic do you get to do for every byte you had to fetch to do
> it?**

Multiply two dense matrices and the answer is enormous: every number you load is
used hundreds of times over, so the arithmetic is the thing you are waiting for.
Add two long lists of numbers and the answer is dismal: load sixteen bytes, do
one addition, move on, and the arithmetic units spend almost all of their time
waiting for the next delivery. Everyone calls this ratio *arithmetic intensity*.

Now count it for the operation this whole guide is about.

Multiplying a sparse matrix by a vector, the way solvers store matrices, costs
about **12 bytes per stored entry**: eight for the value and four to record
which column it sits in. Having fetched that entry, you do **2 operations** with
it: one multiply, one add. Then you never look at it again — there is no reuse
anywhere in the operation, which is exactly what "sparse" costs you.

Two operations per twelve bytes. **0.17 operations per byte.**

That is about as poor as a number of this kind gets, and everything in the next
chapter follows from it.

> **In one sentence.** A sparse matrix-vector product does one sixth of an
> operation per byte it fetches, and nothing about how it is written can change
> that.

---

Chapter 1 of 13

Previous: [What this is](../00-what-this-is/README.md)  
Next: [The roofline](../02-the-roofline/README.md)  
Contents: [lp-on-gpu](../../README.md)
