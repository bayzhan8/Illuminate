# Linear programming duality

*Two problems, one number.*

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
| 0 | [What this is](https://bayzhan8.github.io/Illuminate/lp-duality/#ch0) | two questions, one number |
| 1 | [The workshop](https://bayzhan8.github.io/Illuminate/lp-duality/#ch1) | the region, and why the best plan is a corner |
| 2 | [A good plan cannot prove itself best](https://bayzhan8.github.io/Illuminate/lp-duality/#ch2) | plans give floors, never ceilings |
| 3 | [Charging for the ingredients](https://bayzhan8.github.io/Illuminate/lp-duality/#ch3) | prices, and the ceiling they prove |
| 4 | [Every honest price list is a ceiling](https://bayzhan8.github.io/Illuminate/lp-duality/#ch4) | any honest price list beats every plan |
| 5 | [The gap closes, every time](https://bayzhan8.github.io/Illuminate/lp-duality/#ch5) | the two always meet, on 320 workshops |
| 6 | [Which rules are actually holding you back](https://bayzhan8.github.io/Illuminate/lp-duality/#ch6) | spare resource, zero price |
| 7 | [What one more plank is worth](https://bayzhan8.github.io/Illuminate/lp-duality/#ch7) | where $6.25 actually comes from |
| 8 | [The price is only local](https://bayzhan8.github.io/Illuminate/lp-duality/#ch8) | the price, and its expiry date |
| 9 | [Profit that runs away](https://bayzhan8.github.io/Illuminate/lp-duality/#ch9) | unbounded here means infeasible there |
| 10 | [A plan that cannot exist](https://bayzhan8.github.io/Illuminate/lp-duality/#ch10) | the one-line proof that a plan cannot exist |
| 11 | [Where this leads](https://bayzhan8.github.io/Illuminate/lp-duality/#ch11) | simplex, column generation, Benders |

## The claim this repository makes

Every number on the page is computed, in exact fractions, by the code in
`src/lpduality/`. The tests check three separate things: that the mathematics
is right, that the numbers written in the prose still match what the code
produces, and that the interactive pages compute the same values the Python
does.

```bash
cd .. && make bootstrap   # once, from the repository root
cd lp-duality
make verify               # re-check every number the lesson quotes
make render               # re-render every image
make publish              # regenerate the chapters, the page and the sandboxes
make check                # all three, in that order
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
```

The bundled IBM Plex Mono that makes a clone render identical figures lives once
for the whole repository, in `illuminate/src/illuminate/fonts/`.

The chapter files and the web page are **generated**. Editing them by hand is a
bug, and `make verify` will tell you so.
