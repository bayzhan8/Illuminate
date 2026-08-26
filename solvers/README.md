# What solvers actually do

*What is inside the box, and how to pick one you can actually deploy.*

Hand a solver a twenty-row production model and it deletes thirteen of the rows
and twelve of the columns before any algorithm starts, and settles one of the
yes/no decisions by arithmetic. None of that is simplex and none of it is
branch and bound. Fifteen chapters on the machinery around the algorithm, and
on the part people actually get stuck on: which solvers exist, how they differ,
and which ones you can put in a container without a licence server ruining your
week.

**[Read it →](https://bayzhan8.github.io/Illuminate/solvers/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/solvers/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](https://bayzhan8.github.io/Illuminate/solvers/#ch0) | two thirds of a model, deleted |
| 1 | [A solver is not an algorithm](https://bayzhan8.github.io/Illuminate/solvers/#ch1) | the algorithm is the small part |
| 2 | [What presolve takes out](https://bayzhan8.github.io/Illuminate/solvers/#ch2) | six reductions a person would spot |
| 3 | [The cascade, and where the gap opens](https://bayzhan8.github.io/Illuminate/solvers/#ch3) | why it is a loop and not a checklist |
| 4 | [A decision made by arithmetic](https://bayzhan8.github.io/Illuminate/solvers/#ch4) | a yes/no decision settled by division |
| 5 | [What it costs you](https://bayzhan8.github.io/Illuminate/solvers/#ch5) | a stronger bound, and what it costs |
| 6 | [The rest of the machine](https://bayzhan8.github.io/Illuminate/solvers/#ch6) | cuts, heuristics, branching, numerics |
| 7 | [Who is who](https://bayzhan8.github.io/Illuminate/solvers/#ch7) | who is who among the solvers |
| 8 | [A layer is not a solver](https://bayzhan8.github.io/Illuminate/solvers/#ch8) | a layer is not an engine |
| 9 | [When the problem is not linear](https://bayzhan8.github.io/Illuminate/solvers/#ch9) | squares and norms, and the layer that checks |
| 10 | [What OR-Tools actually is](https://bayzhan8.github.io/Illuminate/solvers/#ch10) | a toolkit, and the one engine in it worth choosing |
| 11 | [Why the benchmarks cannot be read straight](https://bayzhan8.github.io/Illuminate/solvers/#ch11) | the names that left the benchmarks |
| 12 | [Measure on your own models](https://bayzhan8.github.io/Illuminate/solvers/#ch12) | ten of your own instances |
| 13 | [The licence is the deployment problem](https://bayzhan8.github.io/Illuminate/solvers/#ch13) | the licence, not the mathematics |
| 14 | [How to choose](https://bayzhan8.github.io/Illuminate/solvers/#ch14) | the questions in the order they arrive |

## The claim

The presolve here is exact rational arithmetic, and that matters more than
usual. In floating point, "this row can never be violated" quietly becomes
"this row is violated by a millionth", and a reduction that fires on a rounding
error deletes a real solution.

Every reduction is checked against a brute-force enumeration of every whole
point in the model, over four hundred random instances, because presolve is the
part of a solver most capable of being confidently wrong.

The second half of the guide is not computable: it is claims about products and
licences, which change. Those are dated and sourced rather than stated flatly,
and they are the part of this repository most likely to age.

```bash
cd .. && make bootstrap
cd solvers && make check
```
