<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · Three dials

Three, six and fifteen minutes of leftover. Now look back at the ladder in
chapter 6: 27, 54 and 135 minutes of wait.

Every wait in it is exactly nine times the leftover.

The nine is the busy fraction over the idle fraction, 0.9 / 0.1, which is the
only place utilisation gets in at all. Three, six and fifteen minutes of
leftover give 27, 54 and 135, and the two-minutes-and-one-forty-two clerk from
chapter 7 is the fourth row exactly: 9 × 15 = 135. The two rows skipped above
work the same way.

So the wait was never one quantity. It is three, multiplied:

> **wait = (utilisation dial) × (variability dial) × (how long the job takes)**

The last two multiplied together are the leftover of chapter 7, and the first is
the 0.9 / 0.1. Nothing else is in there.

Which makes it a genuine design choice, and the dials do not cost the same to
turn. Buying capacity moves the first one, and near saturation it moves it
brutally slowly, because 0.9 / 0.1 is a ratio that fights back. Making the work
more uniform moves the second one, in direct proportion, at any utilisation at
all. Cutting variability in half does the same thing as a large capacity
increase, and is frequently cheaper.

"Reduce variation" sounds like a slogan. It is arithmetic.

*(The exact version of this is the **Pollaczek–Khinchine** formula, and the
general approximation is **Kingman's**. You can forget both names; the three
dials are the content.)*

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/queues/sandbox/08.html)**
Move utilisation and variability independently and watch which one costs more.

> **In one sentence.** The wait is a product of three separate things, and the
> one everybody manages is the one that is hardest to move.

---

Chapter 8 of 13

Previous: [Why you keep arriving during the long job](../07-the-long-job/README.md)  
Next: [Two clerks, one line](../09-two-clerks/README.md)  
Contents: [queues](../../README.md)
