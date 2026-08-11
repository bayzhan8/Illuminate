<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · A new kind of problem

![A blank plane onto which five constraint lines are added one at a time. Each
new line cuts away part of the shaded area, and after the fifth the survivor is
a five-sided region with its corners marked.](the-region.gif)

Nobody drew that region. It is what is left after each rule takes its cut, and
its corners are simply the places where two rules run out at the same moment.
That is worth dwelling on, because every method in this guide is in some sense
an opinion about those corners: whether to visit them, avoid them, or ignore
them entirely.

The problem itself is old in the way that arithmetic is old. What was new in
the 1940s was treating it as a *computational* question with a general method
attached, rather than as a modelling exercise to be hand-solved case by case.

**1939, Leningrad.** Leonid Kantorovich, asked by a plywood trust how to
allocate work across machines, wrote up a general treatment of what he called
problems of organising and planning production. It contained the essential
ideas, including the multipliers that we would now call dual prices. It was
published in the Soviet Union and went essentially unread in the West for well
over a decade.

**1947, Washington.** George Dantzig, working on planning problems for the US
Air Force, devised the simplex method. The word *programming* here has nothing
to do with computers: a *programme* was a schedule or plan of activities, and a
linear programme was one whose rules and objective were all linear.

Dantzig later wrote that he took the problem to John von Neumann, who on being
shown it stood at a blackboard and lectured him for over an hour on what turned
out to be duality theory, drawing on his work on games. It is a famous story
and it may well be exactly right, but the account is Dantzig's own recollection
and is not independently documented; treat it as such.

The recognition landed unevenly. In 1975 the Sveriges Riksbank Prize in
Economic Sciences went to Kantorovich and T. C. Koopmans for the theory of
optimal allocation of resources. Dantzig, whose method was by then running on
every serious computer in the world, was not among the recipients. He received
the National Medal of Science that same year.

> **In one sentence.** The region and its corners are consequences of the
> rules, not choices anybody made, and the question from 1947 onwards was what
> to do about them.

---

Chapter 1 of 10

Previous: [What this is](../00-what-this-is/README.md)  
Next: [Along the edge](../02-along-the-edge/README.md)  
Contents: [corners-vs-centre](../../README.md)
