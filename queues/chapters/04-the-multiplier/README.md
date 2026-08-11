<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · Where the multiplier comes from

Little's law relates the averages. It does not say how big they are. For that
you have to know something about the randomness, and here the guide stops
proving things and starts quoting one:

> **time in the building = service time × 1/(fraction of time idle)**

That line deserves a warning label. Chapter 2 needed no assumptions at all;
this one needs three, and they are the ones chapter 3 spent a page celebrating the
absence of: customers arrive at random with no rhythm to them, service times
are random in the particular way where knowing a job has already run five
minutes tells you nothing about how much longer it has to go, and there is
exactly one clerk. Queueing theory calls that combination M/M/1. Getting from
those assumptions to that line takes probability this guide does not assume, so
the line is quoted rather than earned.

What can be shown without any probability is why the *idle* fraction ends up
underneath.

Stop watching the queue and watch the backlog. The clerk is 90% busy, which is
another way of saying work walks in at nine tenths of the speed the clerk can
clear it. Serve one customer: six minutes. During those six minutes, more work
arrived: nine tenths of six minutes of it, which is 5.4 minutes. Serve that,
and during those 5.4 minutes another 4.86 minutes walks in. Serve that. Each
round of serving drags in a smaller round of arrivals, and the clerk does not
get to sit down until the whole chain runs out:

> 6 + 5.4 + 4.86 + ... = 6 / (1 − 0.9) = 60 minutes

That is a geometric series. Every term is nine tenths of the one before it, and
a series like that totals the first term divided by whatever is left when you
subtract the ratio from one. The leftover here is the idle fraction. At 90% busy
the chain runs to ten times the original six minutes; at 99% busy, to a hundred
times. Nothing in that calculation is about the clerk's speed. The speed is the
6 at the front. The idle fraction is the multiplier, and it is doing all the
damage.

Strictly, the number that series computes is the length of one unbroken busy
stretch, not one customer's wait. But the 1/(idle fraction) sits in both, and
it is there for the same reason, and for one clerk with random arrivals the two
happen to land on the same sixty minutes.

> **In one sentence.** Each round of serving drags in a smaller round of
> arrivals, and the chain of rounds runs to the service time divided by the
> idle fraction.

---

Chapter 4 of 13

Previous: [What the law does not need](../03-what-it-does-not-need/README.md)  
Next: [The wait explodes before the clerk is full](../05-the-wait-explodes/README.md)  
Contents: [queues](../../README.md)
