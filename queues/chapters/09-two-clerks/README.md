<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 9 · Two clerks, one line

Two clerks, the same total work. Either two separate lines, one per clerk, or a
single line feeding whichever clerk frees up first. Identical staff, identical
capacity, identical utilisation.

![How many times shorter the single-line wait is, as a function of how busy the
clerks are: over three times better when quiet, falling toward twice as good
when busy.](pooling.png)

At 90% busy: **54 minutes** in separate lines, **25.6 minutes** in one line.
Twice as good, for free.

At 45% busy: **4.9 minutes** against **1.5 minutes**. Over three times better.

Note which way round that goes, because most people guess the opposite.
**Pooling helps most when you are quiet**, and its advantage shrinks toward a
factor of two as you get busy.

The mechanism is not extra capacity; there isn't any. It is the elimination of
one specific situation: a clerk sitting idle while somebody waits in the other
line. That situation is pure waste, it is the only thing separate lines can do
that a shared line cannot, and pooling removes all of it.

Which is also why the gain shrinks as you get busier. At 90% busy an idle clerk
is a rare event to begin with, so there is very little of it left to eliminate.
Pooling is worth most exactly when you feel you need it least.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/queues/sandbox/09.html)**
Add clerks and watch the single line pull ahead, then make them busier and
watch the gap close again.

> **In one sentence.** One line for many clerks wins by deleting idle servers
> rather than by adding capacity, so it helps most when you are quiet.

---

Chapter 9 of 13

Previous: [Three dials](../08-three-dials/README.md)  
Next: [When pooling is the wrong answer](../10-when-pooling-loses/README.md)  
Contents: [queues](../../README.md)
