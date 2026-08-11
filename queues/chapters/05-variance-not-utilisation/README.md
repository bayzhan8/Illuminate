<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · It is not the utilisation, it is the variability

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

The reason is not obvious, and the smallest possible example makes it obvious.

Give this clerk two kinds of job and nothing else. Nine customers out of every
ten need two minutes. The tenth needs forty-two. Nothing about the desk has
changed: (9 × 2 + 42) / 10 = 60 / 10 = 6, so the average job is still six
minutes and the clerk is still 90% busy.

Now walk in at a random moment and find the clerk mid-job. Which job is it?
Those ten customers occupy the clerk for 9 × 2 = 18 minutes of short work and
42 minutes of long work, 60 minutes in total. Forty-two of those sixty minutes
are inside the long job. So seven times out of ten you have walked in on the
forty-two-minute customer, even though only one customer in ten is one.

That is the inspection paradox, and it has nothing to do with queues. Sample a
timeline by picking a moment rather than by picking an item, and long items get
picked in proportion to how long they are. The clock is not counting customers.
It is counting minutes, and the long customer brought more of them.

So average the job you land in the way the clock weights it, not the way the
customer list does:

> (18/60) × 2 + (42/60) × 42 = 0.6 + 29.4 = 30 minutes

Thirty. Five times the six-minute average job. You arrive somewhere in the
middle of it, so what is left to run when you sit down is about fifteen
minutes, against the three minutes you would have guessed by halving the
average job and stopping there.

Run that same weighting on the exponential clerk and the leftover comes to six
minutes. On the perfectly regular clerk, where every job is six minutes and
there is nothing for the clock to be biased toward, it is three. Three, six,
fifteen. Now look back at the ladder: 27, 54, 135. Every wait in it is nine
times the leftover, and the nine is the busy fraction over the idle fraction,
0.9 / 0.1, which is the only place utilisation gets in. Three, six and fifteen
minutes of leftover give 27, 54 and 135, and the two-minute-and-forty-two
clerk is the fourth row exactly: 9 × 15 = 135. The two rows I skipped work the
same way.

Which gives three separate dials, and it is a genuine design choice which to
turn:

> **wait = (utilisation dial) × (variability dial) × (how long the job takes)**

The last two multiplied together are the leftover we just computed, and the
first is the 0.9 / 0.1. Nothing else is in there.

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
