<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · Why nobody ever meets one

Now the question chapter 3 left standing, and it has become sharper rather than
easier. Bad cases are not a quirk of one rule. They are everywhere in the
theory. And they are nowhere in practice.

The resolution came from Daniel Spielman and Shang-Hua Teng in 2004, and it is
called **smoothed analysis**. It changes the question being asked.

Worst-case analysis asks: over all inputs of this size, what is the largest
number of pivots? Smoothed analysis asks something the machine can actually be
handed: take any input at all, including a Klee-Minty cube, jiggle every number
in it by a tiny random amount, and now ask for the expected number of pivots.

The answer is polynomial.

Read what that does to the cube. The cube is not merely rare. It is *unstable*:
the exponential behaviour depends on its faces tilting at exactly the angles
Klee and Minty chose, and a perturbation too small to see destroys it. The bad
cases are real and they are knife-edges, and real data — measured quantities,
prices, capacities, anything that arrived with noise on it — is never sitting on
a knife-edge.

So the seventy-year puzzle was not that the theory was wrong. It was that
worst-case analysis had been answering a question whose answer says very little
about the inputs anybody actually has.

> **In one sentence.** The bad cases survive every rule but not a random nudge,
> which is why they fill the theory and never arrive in the post.

---

Chapter 8 of 14

Previous: [Every rule has a cube](../07-every-rule-has-a-cube/README.md)  
Next: [Polynomial, and slower](../09-polynomial-and-slower/README.md)  
Contents: [corners-vs-centre](../../README.md)
