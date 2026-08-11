<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · The wait explodes long before the clerk is full

Little's law relates the averages. It does not say how big they are. For that
you need to know something about the randomness, and with random arrivals and
random service times the answer is:

> **wait = service time × 1/(fraction of time idle)**

![The average wait against utilisation: barely moving up to about 70%, then
bending sharply and going vertical as the idle fraction approaches
zero.](explode.png)

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

This is also why a dashboard that reports utilisation and calls 97% green is
reporting the one number that cannot go bad. Utilisation is bounded above by
one. The wait is bounded by nothing.

> **In one sentence.** The wait is the service time divided by the *idle*
> fraction, so the last sliver of spare capacity carries the whole queue.

---

Chapter 4 of 8

Previous: [What the law does not need](../03-what-it-does-not-need/README.md)  
Next: [It is not the utilisation](../05-variance-not-utilisation/README.md)  
Contents: [queues](../../README.md)
