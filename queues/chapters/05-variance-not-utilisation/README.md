<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · It is not the utilisation, it is the variability

Here is the part that changes what you would actually do.

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

Not roughly half. Half at every utilisation, exactly. And the ladder continues
in the other direction:

| service times are | wait at 90% busy |
|---|---|
| always exactly 6 minutes | **27 min** |
| mildly variable | 40.5 min |
| exponential (the textbook case) | **54 min** |
| some customers much longer | 135 min |
| a few enormously longer | **702 min** |

Same clerk. Same average service time. Same 90% utilisation. A **twenty-six
fold** spread in how long people wait.

The reason is worth knowing, because it is not obvious. When you arrive and
someone is already being served, you wait out the *remainder* of their job.
A random moment is more likely to land inside a long job than a short one,
simply because long jobs occupy more of the timeline. So the job you are stuck
behind is not an average job. It is biased toward the long ones, and the
strength of that bias is exactly the variability of the service times.

Which gives three separate dials, and it is a genuine design choice which to
turn:

> **wait = (utilisation dial) × (variability dial) × (how long the job takes)**

Cutting variability in half does the same thing as a large capacity increase,
and is frequently cheaper. "Reduce variation" sounds like a slogan. It is
arithmetic.

*(The exact version of this is the **Pollaczek–Khinchine** formula, and the
general approximation is **Kingman's**. You can forget both names; the three
dials are the content.)*

> **In one sentence.** At fixed speed and fixed utilisation, how irregular the
> work is can change the wait by a factor of twenty-six.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/queues/sandbox/05.html)**
Move utilisation and variability independently and watch which one costs more.

---

Chapter 5 of 8

Previous: [The wait explodes before the clerk is full](../04-the-wait-explodes/README.md)  
Next: [Two clerks, arranged two ways](../06-two-clerks/README.md)  
Contents: [queues](../../README.md)
