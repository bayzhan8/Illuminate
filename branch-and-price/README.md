# Column generation and branch-and-price

*Solving a problem you never wrote down.*

An order of boards takes seven. Finding a way to cut it in seven is easy;
proving that six is impossible is the whole difficulty, and how well you can
prove it depends entirely on how the question was written down. The way that
works needs one unknown per way of cutting a board — six here, four trillion
for a paper mill — and this is the method that solves it without writing more
than a handful of them down.

The idea is the one from [lp-duality](../lp-duality/), turned into an
algorithm. A set of prices is a certificate that no plan beats your number. So
if the prices *fail* to cover some option, that option is precisely the
variable your model is missing — you do not have to search for it, you can ask
for it.

**[Read it as one page →](https://bayzhan8.github.io/Illuminate/branch-and-price/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch0) | two hand-checkable proofs, 5.44 and 6.5 |
| 1 | [The order](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch1) | boards, pieces, and what a pattern is |
| 2 | [The obvious model, and why it is too weak](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch2) | the obvious model, relaxed into uselessness |
| 3 | [One variable per pattern](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch3) | one variable per pattern, and 6.5 |
| 4 | [Too many to write down](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch4) | four trillion columns |
| 5 | [Start with a few](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch5) | start with three patterns and 7 boards |
| 6 | [What the prices are telling you](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch6) | the prices judge a pattern nobody wrote |
| 7 | [The same test, from the other side](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch7) | the same test, read from the dual side |
| 8 | [Asking for a pattern is a knapsack](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch8) | the missing column is a knapsack |
| 9 | [The loop, and why it is allowed to stop](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch9) | the loop, and why it may stop |
| 10 | [Branching, when the answer is 6.5 boards](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch10) | the loop inside a tree, and two real bugs |
| 11 | [Where this leads](https://bayzhan8.github.io/Illuminate/branch-and-price/#ch11) | Dantzig-Wolfe, Benders, and a warning |

## The claim

Every number on the page is computed in exact fractions by the code in
`src/bandp/`, which reuses the simplex from the duality topic rather than
carrying a second copy — this topic really is that one under load.

Two independent checks do the real work. Column generation is verified against
solving the master over *every* pattern, and branch-and-price against
brute-force integer optimisation over every pattern. Both are hopeless at any
real size, which is the point: they only run on instances small enough that the
slow honest way still finishes.

That check earned its keep. The first version of the search disagreed with
brute force on **476 of 1230** instances, for two reasons that are now written
up in chapter 10 because neither of them announces itself.

```bash
cd .. && make bootstrap   # once, from the repository root
cd branch-and-price
make verify
make check                # render, then publish, then verify
```

## Source

The cutting-stock treatment follows the spirit of chapters 2.2 and 8 of
*Integer Programming*, Conforti, Cornuéjols and Zambelli.
