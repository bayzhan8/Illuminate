<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · It is not the utilisation, it is the variability

So far everything has said the wait comes from how busy the clerk is. That is
half of it, and the smaller half.

Take the desk at 90% busy, where people wait 54 minutes. Change nothing about
the speed: the clerk still averages six minutes a customer, still serves ten an
hour, still busy exactly 90% of the time. Only make the six minutes *reliable*
so that every customer takes exactly six minutes, no more and no less.

The wait falls to **27 minutes**. Exactly half.

![Left, the wait at 90% busy for five different levels of service variability,
from 27 minutes when every job is identical to 702 minutes when a few are
enormously longer. Right, two curves against utilisation, the constant-service
one exactly half the variable one at every
point.](variance.png)

Half at every utilisation, exactly, and not approximately. The ladder continues
in the other direction too:

| service times are | wait at 90% busy |
|---|---|
| always exactly 6 minutes | **27 min** |
| mildly variable | 40.5 min |
| exponential (the textbook case) | **54 min** |
| some customers much longer | 135 min |
| a few enormously longer | **702 min** |

Same clerk. Same average service time. Same 90% utilisation. A **twenty-six
fold** spread in how long people wait.

Nothing in chapter 4 predicts that. The formula there had a service time and an
idle fraction in it, and both are being held fixed across every row of that
table. Something else is setting the wait, and the next two chapters are about
what.

> **In one sentence.** Two desks can be identical in speed and identical in how
> busy they are, and still differ twenty-six fold in how long you queue.

---

Chapter 6 of 13

Previous: [The wait explodes before the clerk is full](../05-the-wait-explodes/README.md)  
Next: [Why you keep arriving during the long job](../07-the-long-job/README.md)  
Contents: [queues](../../README.md)
