# Linear programming duality

*Every plan has a price tag.*

Every planning problem comes with a second problem attached to it, about
prices, and solving either one solves both. That fact is why a solver can tell
you what a resource is worth rather than only what to do with it, and it is the
machinery inside column generation, Benders decomposition and everything built
on them.

This guide builds it from a workshop with three shelves and two products, and
never writes an equation.

**[Read it as one page →](https://bayzhan8.github.io/Illuminate/lp-duality/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](chapters/00-what-this-is/) | two problems, one number |
| 1 | [The workshop](chapters/01-the-workshop/) | the problem, and its picture |
| 2 | [A good plan cannot prove itself best](chapters/02-no-way-to-check/) | searching never certifies |
| 3 | [Charging for the ingredients](chapters/03-mixing-the-rules/) | where a ceiling comes from |
| 4 | [Every honest price list is a ceiling](chapters/04-every-mix-is-a-ceiling/) | weak duality, in two steps |
| 5 | [The gap closes, every time](chapters/05-the-gap-closes/) | strong duality |
| 6 | [Which rules are holding you back](chapters/06-who-is-binding/) | complementary slackness |
| 7 | [What one more plank is worth](chapters/07-what-one-more-is-worth/) | shadow prices |
| 8 | [The price is only local](chapters/08-the-price-breaks/) | and how local |
| 9 | [When it goes wrong](chapters/09-when-it-goes-wrong/) | unbounded, impossible, degenerate |
| 10 | [Where this leads](chapters/10-where-this-leads/) | the next four topics |

## The claim this repository makes

Every number on the page is computed, in exact fractions, by the code in
`src/lpduality/`. The tests check three separate things: that the mathematics
is right, that the numbers written in the prose still match what the code
produces, and that the interactive pages compute the same values the Python
does.

```bash
cd .. && make venv     # once
cd lp-duality
make test              # re-check every number the lesson quotes
make figures           # re-render every image
make build             # regenerate the chapters, the page and the sandboxes
```

## Layout

```
lesson.md      the prose, and the only place it exists
build.py       lesson.md -> chapter files, the web page, the sandboxes
chapters/      one folder per chapter: a generated README and its images
figures/       one script per chapter, writing into chapters/
sandbox/       generated pages you can push around, no server needed
src/lpduality/ the exact-arithmetic solver and everything derived from it
tests/         the maths, the prose-against-the-code, the JS-against-the-Python
notes/         why it is built the way it is
assets/fonts/  IBM Plex Mono, so a clone renders identical figures
```

The chapter files and the web page are **generated**. Editing them by hand is a
bug, and `make test` will tell you so.
