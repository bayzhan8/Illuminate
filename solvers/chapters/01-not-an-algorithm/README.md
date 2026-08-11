<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · A solver is not an algorithm

If you have read the other guides here, you know how to solve a linear program.
[Walk the corners](../corners-vs-centre/), or go through the middle. You could
implement one. People do, in a few hundred lines.

What you would have is not a solver, and the gap is not a matter of polish.

A commercial mixed-integer solver is perhaps a million lines. The part that
takes a step, the simplex pivot or the interior point iteration, is a small
fraction of it. The rest is:

| the part | what it is for |
|---|---|
| **presolve** | shrink the model before touching it, and tighten what remains |
| **postsolve** | turn an answer to the shrunken model back into an answer to yours |
| **scaling** | rewrite the numbers so the arithmetic does not fall apart |
| **cutting planes** | add constraints that cut off fractions without cutting off answers |
| **heuristics** | find a good solution early, so the search has something to prune against |
| **node selection** | decide which part of the search tree to look at next |
| **branching rules** | decide what to split on, which matters more than almost anything |
| **restarts** | throw the tree away and start again with what you learned |
| **tolerances** | decide what counts as zero, which is a policy question, not a fact |
| **the algorithm** | the pivots or the Newton steps |

The last row is the one in the textbooks. It is not where the difference
between a solver that finishes and one that does not usually lives.

There is a well-known measurement of this. Robert Bixby tracked linear
programming speed from 1988 to 2004 and separated the two causes: machines got
about a thousand times faster, and the algorithms and implementations got about
**3,300 times faster on top of that**. Thorsten Koch and colleagues repeated
the exercise for 2001 to 2020 and found the machine-independent factor had
continued to climb, more slowly for LP and considerably faster for
mixed-integer problems.

Machine-independent means exactly what it says. Same computer, same model, same
answer, thousands of times sooner, because of what the software decided to do
before and around the arithmetic.

> **In one sentence.** The algorithm is the part you can write down, and it is
> a minority of what makes a solver fast.

---

Chapter 1 of 14

Previous: [What this is](../00-what-this-is/README.md)  
Next: [What presolve takes out](../02-what-it-removes/README.md)  
Contents: [solvers](../../README.md)
