<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 13 · The same law somewhere else entirely

Little's law says nothing about queues. It says something about boxes with
things going in and out. Rename the three letters:

| | L | λ | W |
|---|---|---|---|
| a queue | customers present | arrivals per hour | time in the system |
| **inventory** | stock on hand | throughput | days of supply |
| **a factory** | work in progress | production rate | cycle time |
| **a kanban board** | items in progress | delivery rate | lead time |
| **a hospital ward** | occupied beds | admissions per day | length of stay |
| **a company** | employees | hires per year | average tenure |

Each row is the same theorem. Two are worth spelling out.

**A WIP limit is a lead-time limit.** A team finishing 12 items a week with 6
in progress has a lead time of 6/12 = half a week. Raise the limit to 18 "so
nobody is blocked" and throughput does not move, being set by the bottleneck
rather than by how much you shove in, so the lead time becomes 18/12, a week
and a half. It tripled, and nothing else about the team changed. This is the entire
theoretical content of a kanban limit, and of CONWIP, the older
constant-work-in-progress rule it descends from.

**Safety stock is measured in time, whether you like it or not.** A distributor
moving $100,000 of goods a day and holding $9M of inventory has, by Little's
law, 90 days of supply. Add $3M of stock to improve service and you have not
bought service; you have bought 30 more days of age on every unit. Obsolescence
and markdown scale with `W`, and you just increased it by a third.

Neither of those needed a demand distribution, a lead-time model, or an
independence assumption. That is why this particular result survives contact
with reality when most inventory theory does not.

> **In one sentence.** Anything with a boundary, an inflow and an outflow obeys
> the same identity, which is why a WIP limit and a days-of-supply figure are
> the same statement twice.

## What the plain words are really called

| this guide says | everyone else says |
|---|---|
| how many are here, on average | **L**, the time-average number in system |
| how long a person is here | **W**, the customer-average sojourn time |
| L = λW | **Little's law** |
| fraction of time the clerk is busy | utilisation, **ρ** |
| one over the idle fraction | the congestion multiplier, 1/(1−ρ) |
| random arrivals, random service, one clerk | **M/M/1** |
| every job takes exactly the same time | **M/D/1** |
| the variability dial | the squared coefficient of variation, **c²** |
| the wait formula for any service distribution | the **Pollaczek–Khinchine** formula |
| the three-dial version | **Kingman's** approximation |
| one line, several clerks | **M/M/c**; the wait probability is **Erlang C** |
| cutting a run into blocks to get an honest interval | the **batch means** method |

## Further reading

Ross's *Introduction to Probability Models* for the derivations, Harchol-Balter's
*Performance Modeling and Design of Computer Systems* for the many-server and
job-size-variability material, and Little's own 50th-anniversary retrospective
for how far the identity reaches. The sample-path proof in chapter 2 follows
Stidham's 1974 version, which is the one that needs no probability.

## Running the code

```bash
make bootstrap    # once, from the repository root
cd queues && make verify
```

The formulas are exact rationals, so "exactly half" in chapter 6 means exactly
half. The simulation shares no code with the formulas, which is what lets the
tests use each to check the other.

---

Chapter 13 of 13

Previous: [The confidence interval is twenty times too narrow](../12-coverage/README.md)  
Contents: [queues](../../README.md)
