<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · Not cycling is not the same as being fast

Bland's rule is the one to be careful about, because it is easy to draw the
wrong lesson from it.

Its guarantee is that it cannot cycle. A simplex walk can in principle return
to a corner it has already left and go round forever; Bland's rule makes that
impossible, so the walk always terminates. That is a real property, and it is
why the other guides in this repository use it.

Termination is not speed, and here the difference can be measured exactly.

Start with the formula, since it arrives out of nowhere. The Fibonacci numbers
are what you get by starting with 1 and 1 and making every term the sum of the
two before it: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, and on up. Bland's count on
the cube of dimension *n* is the term at position *n* + 1, doubled, less one. At
n = 10 the term is 89, so the count is 177.

Now watch what that does as the cube grows. The counts run
3, 5, 9, 15, 25, 41, 67, 109, 177. Divide each by the one before it. 5 over 3 is
one and two thirds; 9 over 5 is 1.8; 15 over 9 is back to one and two thirds.
They bounce about at first. Then they settle: by 109 over 67 they have almost
stopped moving, and 177 over 109 sits a whisker above 1.6 and is still edging
down.

What they are closing in on is the golden ratio, about 1.618, which is what
ratios of consecutive Fibonacci numbers always do. So each extra dimension
multiplies Bland's pivot count by about 1.618, where Dantzig's rule multiplies
by 2. Both are exponential. One simply has a smaller base, and a smaller base
buys you a few dimensions, not a different answer. Avis and Chvátal established
this in 1978.

**Not cycling is not the same as being fast.** The cube is what lets that be
shown rather than asserted, and it is the reason a guarantee should always be
read for what it actually promises.

> **In one sentence.** Bland's rule promises that the walk will finish, not that
> it will finish soon, and on the cube its count still multiplies by about 1.618
> for every dimension added.

---

Chapter 6 of 14

Previous: [The rule, not the method](../05-not-the-rule/README.md)  
Next: [Every rule has a cube](../07-every-rule-has-a-cube/README.md)  
Contents: [corners-vs-centre](../../README.md)
