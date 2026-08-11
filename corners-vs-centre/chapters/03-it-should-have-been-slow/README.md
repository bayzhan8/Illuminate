<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · It should have been slow

![A logarithmic chart against the number of variables. One line, for the number
of corners a search would face, climbs steeply off the top of the chart. A band
near the bottom, for the number of hops solves are observed to take, stays
almost flat.](the-count.png)

Here is the arithmetic that should have killed the method in its first week.

A corner is where enough rules run out at once: with *n* variables, pick *n* of
the rules and solve them as simultaneous equations. Every corner arises that
way, so counting corners is really counting the ways of choosing which rules
run out.

Take a problem with 30 variables and twice as many rules. A corner is then a
choice of 30 rules out of the 60 available, and the number of corners cannot
exceed the number of such choices: how many different committees of 30 you can
pick from 60 candidates. That count has a name and a notation, C(60, 30), read
aloud as "sixty choose thirty". At 30 variables it is about **1.18 × 10¹⁷**. A
hundred million billion, near enough.

Thirty variables is a toy. Real models have millions. If the walk had to see
any appreciable fraction of the corners, the method would be useless at any
size worth caring about.

It does not. In practice the number of hops tends to come out at a small
multiple of the number of *rules*, which is a number you can afford. That has
been the observed behaviour since the 1950s, on essentially everything anyone
has thrown at it. (The band drawn above is that rule of thumb, not a
measurement from this repository.)

So the method worked, spectacularly, and nobody could say why. Two questions
sat open:

- **Is there a bad case?** Some input on which the walk really does visit an
  exponential number of corners.
- **If bad cases exist, why does nobody ever meet one?**

The first was answered in 1972. The second took until 2004.

> **In one sentence.** The corner count says the walk should be impossible, and
> for twenty-five years the only evidence against that was that it kept
> working.

---

Chapter 3 of 14

Previous: [Along the edge](../02-along-the-edge/README.md)  
Next: [Klee and Minty build a cube](../04-the-cube/README.md)  
Contents: [corners-vs-centre](../../README.md)
