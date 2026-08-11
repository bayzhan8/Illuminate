<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · Two clerks, arranged two ways

Two clerks, the same total work. Either two separate lines, one per clerk, or a
single line feeding whichever clerk frees up first. Identical staff, identical
capacity, identical utilisation.

![Left, how many times shorter the single-line wait is, as a function of how
busy the clerks are: over three times better when quiet, falling toward twice
as good when busy. Right, a case where dedicating a desk to each job type beats
pooling by a factor of 1.5.](pooling.png)

At 90% busy: **54 minutes** in separate lines, **25.6 minutes** in one line.
Twice as good, for free.

At 45% busy: **4.9 minutes** against **1.5 minutes**. Over three times better.

Note which way round that goes, because most people guess the opposite.
**Pooling helps most when you are quiet**, and its advantage shrinks toward a
factor of two as you get busy. The mechanism is not extra capacity; there
isn't any. It is the elimination of the situation where one clerk sits idle
while somebody waits in the other line. When you are nearly saturated, that
situation is rare anyway, so there is less of it to eliminate.

### When pooling is the wrong answer

Suppose the work is not all alike. Quick jobs take an hour and arrive often;
slow jobs take ten hours and arrive rarely. Give each type its own desk, and
each desk runs at 80% busy. Or pool them into one line served by a desk of
double speed, at identical total capacity and identical utilisation.

| | average wait |
|---|---|
| a desk for quick jobs, a desk for slow ones | **3.64 hours** |
| one line, one desk of double speed | **5.50 hours** |

Pooling is **1.5 times worse**. Nothing was taken away; the arrangement
alone did it. Putting everything in one line means a one-hour job can arrive behind a
ten-hour job and wait for it, and chapter 5 already told us what happens when
you increase the variability of what people are stuck behind.

Pooling raises the number of servers, which helps, and raises the variability
of the queue everyone is standing in, which hurts. Usually the first wins. When
the jobs are wildly different sizes, the second does, which is why hospitals
have a separate minor injuries stream and supermarkets have a basket-only till.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/queues/sandbox/06.html)**
Add clerks and watch the single line pull ahead, then make them busier and
watch the gap close again.

---

Chapter 6 of 8

Previous: [It is not the utilisation](../05-variance-not-utilisation/README.md)  
Next: [Measuring it is harder than computing it](../07-measuring-is-harder/README.md)  
Contents: [queues](../../README.md)
