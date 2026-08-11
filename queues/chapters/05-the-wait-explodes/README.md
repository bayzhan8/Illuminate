<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · The wait explodes long before the clerk is full

Now put numbers through it, because the shape of the answer is not what anybody
expects.

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
one, so it can never look alarming. The wait is bounded by nothing, and by the
time utilisation looks impressive the wait has already left the building.

> **In one sentence.** What runs out as you approach saturation is not capacity
> but slack, so a few percent more work near the top multiplies the wait.

---

Chapter 5 of 13

Previous: [Where the multiplier comes from](../04-the-multiplier/README.md)  
Next: [It is not the utilisation](../06-variance-not-utilisation/README.md)  
Contents: [queues](../../README.md)
