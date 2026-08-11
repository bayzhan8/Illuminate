<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 12 · The confidence interval is twenty times too narrow

Now the part that should worry anyone who has ever reported a simulation result.

Take the ordinary 95% confidence interval, the one every statistics course
teaches, the standard deviation over the square root of the sample size, and
apply it to two hundred thousand measured waits. Repeat the whole experiment
three hundred times, and count how often the interval actually contains the true
answer.

![A nominal 95% confidence interval covering the true answer 9% of the time when
it assumes independence, and 96% when it does
not.](coverage.png)

It contains the true answer **9% of the time**. It is about twenty times
too narrow.

The reason is that consecutive waits in a queue are not independent
observations, and it is not close. One long wait makes the next one long.

You can measure how long that memory lasts, and the code in this folder does.
Simulate six hundred thousand waits in a row. Take each wait and the one after
it and see how strongly the two move together; do the same at a gap of two
customers, and three, and ten, and keep adding those up until the agreement
dies away and the queue has forgotten. The total is how many customers it takes
before you have genuinely learned something new.

At 90% busy, roughly four hundred consecutive customers behave as a single
observation. So two hundred thousand measurements are worth about five hundred.

Roughly is the honest word: run the measurement again on different random
numbers and the answer moves by a hundred either way. But the size is not in
doubt, and note what it was measured from. That number came out of the waits
themselves, with no reference to any confidence interval. The coverage came out
of running the experiment three hundred times and counting. So the square root
of four hundred being twenty, the same factor by which the interval is too
narrow, is two separate measurements landing in the same place rather than one
of them restated.

Cutting the run into ten large blocks and treating the block averages as the
observations restores it: **96% coverage**, with an honest interval more than twenty
times wider than the confident, wrong one.

The moral is not that simulation is useless. It is that near saturation, the
formula is not the approximation. The measurement is.

> **In one sentence.** Little's law being satisfied is not evidence that your
> measurement has converged, and the ordinary confidence interval is twenty
> times too narrow.

---

Chapter 12 of 13

Previous: [Measuring it is harder than computing it](../11-measuring-is-harder/README.md)  
Next: [The same law somewhere else](../13-the-same-law-elsewhere/README.md)  
Contents: [queues](../../README.md)
