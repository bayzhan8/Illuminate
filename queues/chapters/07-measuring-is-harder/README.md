<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · Measuring it is harder than computing it

If you did not believe any of the above, the obvious move is to measure your
own queue. This chapter is about why that is much harder than it looks.

Run a simulated desk at 90% busy and track both averages as they accumulate:
counting heads over time and dividing by the arrival rate, against asking each
customer and averaging.

![Left, two estimates of the average time in the system as a run proceeds, one
riding exactly on top of the other, both wandering between 44 and 60 minutes
over three hundred thousand customers. Right, a nominal 95% confidence interval
covering the true answer 9% of the time when it assumes independence, and 96%
when it does not.](measuring.png)

Two things are in that picture, and they point in opposite directions.

**Little's law is satisfied from almost the first customer.** The two curves
sit on top of each other the whole way. That is the identity of chapter 2
doing its work: over a window that starts and ends with an empty room, the
agreement is exact to fourteen decimal places, with no assumptions and no limit
taken.

**And both of them are wrong for a very long time.** After three hundred
thousand customers the estimate is still wandering around in the fifties for a
true answer of sixty. Your simulation satisfying `L = λW` tells you nothing
whatsoever about whether it has converged. It was never going to fail that
check.

Then the part that should worry anyone who has ever reported a simulation
result. Take the ordinary 95% confidence interval, the one every statistics course
teaches, the standard deviation over the square root of the sample size, and
apply it to a million measured waits. Repeat the whole experiment three
hundred times.

It contains the true answer **9% of the time**. It is about twenty times
too narrow.

The reason is that consecutive waits in a queue are not independent
observations, and it is not close. One long wait makes the next one long.

At 90% busy, roughly four hundred consecutive customers behave as a single
observation. So a million measurements are worth about two and a half thousand.

The square root of four hundred is twenty, which is exactly the factor by which
the interval is wrong.

Cutting the run into ten large blocks and treating the block averages as the
observations restores it: **96% coverage**, with an honest interval more than twenty
times wider than the confident, wrong one.

The moral is not that simulation is useless. It is that near saturation, the
formula is not the approximation. The measurement is.

> **In one sentence.** Little's law being satisfied is not evidence that your
> measurement has converged, and the ordinary confidence interval is twenty
> times too narrow.

---

Chapter 7 of 8

Previous: [Two clerks, arranged two ways](../06-two-clerks/README.md)  
Next: [The same law somewhere else](../08-the-same-law-elsewhere/README.md)  
Contents: [queues](../../README.md)
