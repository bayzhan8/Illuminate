# Column generation and branch-and-price

*Solving a model you never wrote down.*

A model with four trillion variables that fits on a napkin, and a method that
solves it without writing down more than a handful of them.

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
| 0 | [What this is](chapters/00-what-this-is/) | 5.44, 6.5, and the answer 7 |
| 1 | [The order](chapters/01-the-order/) | boards, pieces, and what a pattern is |
| 2 | [The obvious model, and why it is too weak](chapters/02-the-obvious-model/) | the obvious model, relaxed into uselessness |
| 3 | [One variable per pattern](chapters/03-one-variable-per-pattern/) | one variable per pattern, and 6.5 |
| 4 | [Too many to write down](chapters/04-too-many-to-write-down/) | four trillion columns |
| 5 | [Start with a few](chapters/05-start-with-a-few/) | start with three patterns and 7 boards |
| 6 | [What the prices are telling you](chapters/06-what-the-prices-say/) | the prices judge a pattern nobody wrote |
| 7 | [The same test, from the other side](chapters/07-the-same-from-the-dual/) | the same test, read from the dual side |
| 8 | [Asking for a pattern is a knapsack](chapters/08-a-knapsack/) | the missing column is a knapsack |
| 9 | [The loop, and why it is allowed to stop](chapters/09-the-loop/) | the loop, and why it may stop |
| 10 | [Branching, when the answer is 6.5 boards](chapters/10-branch-and-price/) | the loop inside a tree, and two real bugs |
| 11 | [Where this leads](chapters/11-where-this-leads/) | Dantzig-Wolfe, Benders, and a warning |

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
cd .. && make venv
cd branch-and-price
make test
make check     # figures, then build, then test
```

## Source

The cutting-stock treatment follows the spirit of chapters 2.2 and 8 of
*Integer Programming*, Conforti, Cornuéjols and Zambelli.
