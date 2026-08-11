<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · Why you keep arriving during the long job

The reason is not obvious, and the smallest possible example makes it obvious.

Give this clerk two kinds of job and nothing else. Nine customers out of every
ten need two minutes. The tenth needs forty-two. Nothing about the desk has
changed: (9 × 2 + 42) / 10 = 60 / 10 = 6, so the average job is still six
minutes and the clerk is still 90% busy.

Now walk in at a random moment and find the clerk mid-job. Which job is it?

Here is the check worth doing in your head, because it is where the whole
chapter lives. Those ten customers occupy the clerk for 9 × 2 = 18 minutes of
short work and 42 minutes of long work, 60 minutes in total. Forty-two of those
sixty minutes are inside the long job. So seven times out of ten you have walked
in on the forty-two-minute customer, even though only one customer in ten is
one.

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

That leftover is the quantity the next chapter needs. Run the same weighting on
the exponential clerk and it comes to six minutes. On the perfectly regular
clerk, where every job is six minutes and there is nothing for the clock to be
biased toward, it is three.

Three, six, fifteen.

> **In one sentence.** You do not meet the average job; you meet the job that
> was occupying the most minutes, which is why irregular work costs so much.

---

Chapter 7 of 13

Previous: [It is not the utilisation](../06-variance-not-utilisation/README.md)  
Next: [Three dials](../08-three-dials/README.md)  
Contents: [queues](../../README.md)
