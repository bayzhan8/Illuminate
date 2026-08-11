<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · The loop, and why it is allowed to stop

Put the two halves together and they take turns.

> **Column generation**
>
> 1. Start with any set of patterns that can fill the order at all.
> 2. Solve the restricted master. Read off the prices.
> 3. Solve the knapsack at those prices.
> 4. If its best pattern is worth **more than one board**, add it and go to 2.
> 5. Otherwise stop: no pattern in existence would help, so the restricted
>    answer is the full model's answer.

![Four rounds of the loop, each showing what the master needs, the current
prices, and the pattern the knapsack asks for
next.](loop.gif)

Watch the number come down: **7 boards**, then 6.875, then 6.5. Then the
knapsack returns a pattern worth exactly 1 and the loop stops. Three patterns
added, and 6.5 boards is optimal for a model nobody wrote down.

Be exact about what step 5 claims. Not that no better answer exists: that no
*column* exists which would improve this one. The knapsack searched every
pattern implicitly rather than sampling some, so it is a proof.

On a slightly bigger order, 55-foot boards with four different lengths, there
are thirty usable patterns, and the loop settles after touching six of them:

![Thirty patterns drawn as boards, with the six the loop actually built
highlighted and the rest left blank.](touched.png)

Twenty-four patterns were never written down and never needed to be. On the
mill instance the same sentence holds with four trillion in place of
twenty-four.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/07.html)**
Step the loop one round at a time and watch the prices move.

---

Chapter 7 of 9

Previous: [Asking for a pattern is a knapsack](../06-a-knapsack/README.md)  
Next: [Branching, when the answer is 6.5 boards](../08-branch-and-price/README.md)  
Contents: [branch-and-price](../../README.md)
