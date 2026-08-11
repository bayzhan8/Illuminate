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
| 0 | [What this is](chapters/00-what-this-is/) | two thirds of a model, deleted |
| 1 | [A solver is not an algorithm](chapters/01-not-an-algorithm/) | the algorithm is the small part |
| 2 | [What presolve takes out](chapters/02-what-it-removes/) | six reductions a person would spot |
| 3 | [The cascade, and where the gap opens](chapters/03-the-cascade/) | why it is a loop and not a checklist |
| 4 | [A decision made by arithmetic](chapters/04-a-decision-by-arithmetic/) | a yes/no decision settled by division |
| 5 | [What it costs you](chapters/05-what-it-costs/) | a stronger bound, and what it costs |
| 6 | [The rest of the machine](chapters/06-the-rest-of-the-machine/) | cuts, heuristics, branching, numerics |
| 7 | [Who is who](chapters/07-who-is-who/) | who is who among the solvers |
| 8 | [A layer is not a solver](chapters/08-a-layer-not-a-solver/) | a layer is not an engine |
| 9 | [When the problem is not linear](chapters/09-not-linear/) | squares and norms, and the layer that checks |
| 10 | [A toolkit is not a solver either](chapters/10-a-toolkit-is-not-a-solver/) | a toolkit is neither |
| 11 | [Why the benchmarks cannot be read straight](chapters/11-the-benchmarks/) | the names that left the benchmarks |
| 12 | [Measure on your own models](chapters/12-measure-your-own/) | ten of your own instances |
| 13 | [The licence is the deployment problem](chapters/13-the-licence/) | the licence, not the mathematics |
| 14 | [How to choose](chapters/14-how-to-choose/) | the questions in the order they arrive |

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
