<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · The wait explodes long before the clerk is full

Little's law relates the averages. It does not say how big they are. For that
you have to know something about the randomness, and here the guide stops
proving things and starts quoting one:

> **wait = service time × 1/(fraction of time idle)**

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

![The average wait against utilisation: barely moving up to about 70%, then
bending sharply and going vertical as the idle fraction approaches
zero.](explode.png)

Sixty minutes is the whole visit, service included. The table below reports the
wait *before* service starts, so it is the same formula with the six minutes of
actual service taken back off: 60 − 6 = 54. Every row is that subtraction.

| arrivals per hour | busy | people present | wait before service |
|---|---|---|---|
| 5 | 50% | 1 | **6 min** |
| 8 | 80% | 4 | 24 min |
| 9 | 90% | 9 | **54 min** |
| 9.5 | 95% | 19 | 114 min |
| 9.9 | 99% | 99 | **594 min** |

Read the arithmetic between the rows, because it is the whole point:

- **5 to 9 customers an hour.** You added 80% more work. The wait went up
  **nine times**.
- **9 to 9.5.** You added 5.6% more work. The wait **doubled**.
- **9.5 to 9.9.** You added 4.2% more work. The wait went up **five times**.

The multiplier is one over the *idle* fraction, so what is being consumed as
you approach saturation is not capacity but slack. At 99% busy, the last one
percent of the clerk's time is carrying all of the queue.

The middle column is chapter 2 again, quietly checking the work. Nine arrivals
an hour, an hour in the building each, so `L = λW` says nine people should be
standing there on average. They are.

This is also why a dashboard that reports utilisation and calls 97% green is
reporting the one number that cannot go bad. Utilisation is bounded above by
one. The wait is bounded by nothing.

> **In one sentence.** This one is quoted, not proved: time in the building is
> the service time divided by the *idle* fraction, so the last sliver of spare
> capacity carries the whole queue.

---

Chapter 4 of 8

Previous: [What the law does not need](../03-what-it-does-not-need/README.md)  
Next: [It is not the utilisation](../05-variance-not-utilisation/README.md)  
Contents: [queues](../../README.md)
