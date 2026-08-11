# Column generation and branch-and-price

*Ask the prices what you are missing.*

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
| 0 | [What this is](chapters/00-what-this-is/) | two relaxations, one order |
| 1 | [The order](chapters/01-the-order/) | cutting stock, and what a pattern is |
| 2 | [The obvious model](chapters/02-the-obvious-model/) | and why it is too weak |
| 3 | [One variable per pattern](chapters/03-one-variable-per-pattern/) | integrality absorbed into the variables |
| 4 | [Too many to write down](chapters/04-too-many-to-write-down/) | four trillion of them |
| 5 | [Let the prices ask](chapters/05-let-the-prices-ask/) | the restricted master, and reduced cost |
| 6 | [Asking is a knapsack](chapters/06-a-knapsack/) | the pricing problem |
| 7 | [The loop](chapters/07-the-loop/) | and why it is allowed to stop |
| 8 | [Branching](chapters/08-branch-and-price/) | branch-and-price, and two traps |
| 9 | [Where this leads](chapters/09-where-this-leads/) | Dantzig–Wolfe, Benders, pre-generated columns |

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
up in chapter 8 because neither of them announces itself.

```bash
cd .. && make venv
cd branch-and-price
make test
make check     # figures, then build, then test
```

## Source

The cutting-stock treatment follows the spirit of chapters 2.2 and 8 of
*Integer Programming*, Conforti, Cornuéjols and Zambelli.
