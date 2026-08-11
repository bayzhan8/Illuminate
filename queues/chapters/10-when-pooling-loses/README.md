<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · When pooling is the wrong answer

Chapter 9 makes pooling sound unconditional. It is not, and chapter 8 already
handed you the reason it can fail.

Suppose the work is not all alike. Quick jobs take an hour and arrive often;
slow jobs take ten hours and arrive rarely. Give each type its own desk, and
each desk runs at 80% busy. Or pool them into one line served by a desk of
double speed, at identical total capacity and identical utilisation.

![Two bars at identical total capacity and identical utilisation: a desk for
quick jobs and a desk for slow ones waits 3.64 hours, while one line served by
a desk of double speed waits 5.50 hours.](dedicated.png)

| | average wait |
|---|---|
| a desk for quick jobs, a desk for slow ones | **3.64 hours** |
| one line, one desk of double speed | **5.50 hours** |

Pooling is **1.5 times worse**. Nothing was taken away; the arrangement alone
did it.

Read it through the three dials. Putting everything in one line means a
one-hour job can arrive behind a ten-hour job and wait for it, so the *thing
people queue behind* has become wildly more irregular. That is the second dial
of chapter 8, turned the wrong way, and chapter 7 is why it hurts: arrive at a
random moment and you are far more likely to land inside a ten-hour job than a
count of the jobs would suggest.

So pooling does two things at once. It raises the number of servers, which
helps, and it raises the variability of the single queue everyone now stands
in, which hurts. Usually the first wins. When the jobs are wildly different
sizes, the second does, which is why hospitals have a separate minor injuries
stream and supermarkets have a basket-only till.

> **In one sentence.** Pooling trades more servers against a more irregular
> queue, and when job sizes differ wildly that trade goes the wrong way.

---

Chapter 10 of 13

Previous: [Two clerks, one line](../09-two-clerks/README.md)  
Next: [Measuring it is harder than computing it](../11-measuring-is-harder/README.md)  
Contents: [queues](../../README.md)
