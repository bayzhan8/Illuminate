<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 11 · Measuring it is harder than computing it

If you did not believe any of the above, the obvious move is to measure your
own queue. This chapter is about why that is much harder than it looks.

Run a simulated desk at 90% busy and track both averages as they accumulate:
counting heads over time and dividing by the arrival rate, against asking each
customer and averaging.

![Two estimates of the average time in the system as a run proceeds, one riding
exactly on top of the other, both wandering between 44 and 60 minutes over
three hundred thousand customers.](measuring.png)

Two things are in that picture, and they point in opposite directions.

**Little's law is satisfied from almost the first customer.** The two curves
sit on top of each other the whole way. That is the identity of chapter 2
doing its work: over a window that starts and ends with an empty room, the
agreement is exact to fourteen decimal places, with no assumptions and no limit
taken.

**And both of them are wrong for a very long time.** After three hundred
thousand customers the estimate is still wandering around in the fifties for a
true answer of sixty.

Put those together and you get the trap. Your simulation satisfying `L = λW`
tells you nothing whatsoever about whether it has converged, because it was
never going to fail that check. The identity holds on any sample path at all,
converged or not — that is precisely what chapter 3 was celebrating. A test that
cannot fail is not evidence.

So the reassuring thing your run reports is the one thing that carries no
information about the number you care about.

> **In one sentence.** Little's law is satisfied long before your estimate is
> right, so watching it agree tells you nothing about whether you can stop.

---

Chapter 11 of 13

Previous: [When pooling is the wrong answer](../10-when-pooling-loses/README.md)  
Next: [The confidence interval is twenty times too narrow](../12-coverage/README.md)  
Contents: [queues](../../README.md)
