<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 13 · The licence is the deployment problem

Here is the part nobody warns you about, and it is where most of the pain
actually is. The mathematics never fails on a Friday. The licence does.

A commercial solver has to check that you are allowed to run it, and how it
checks is the whole story.

**Node-locked.** A file tied to one machine, usually by its MAC address or host
ID. Fine on a laptop. Useless the moment your workload lives on machines that
did not exist this morning, because the identity it is locked to is the thing
your infrastructure keeps replacing.

**Floating.** A licence server on your network hands out tokens, and you pay for
how many are checked out at once. This works, and it requires that every worker
can reach that server, which turns a maths library into a piece of network
architecture with a firewall rule and a single point of failure.

**Cloud and container licensing.** This is the modern answer and the reason the
old pain has eased. Gurobi's **Web License Service** issues short-lived signed
tokens to a container over the internet, renewed automatically, configured
either by mounting a `gurobi.lic` file or by setting three environment
variables: `GRB_WLSACCESSID`, `GRB_WLSSECRET` and `GRB_LICENSEID`. That last
form is what makes a solver deployable on Kubernetes at all, because the
credential becomes a secret like every other secret. The other vendors have
their own equivalents.

If you have fought a solver licence in a container, this is almost certainly
what you were fighting: a node-locked or floating scheme meeting an environment
where machines are disposable and there is no stable host to lock to. The fix is
generally not a cleverer Dockerfile. It is a different licence type.

**Academic licences** are genuinely generous and genuinely restricted. They are
free, they are usually full-strength, and they are for academic work. Using one
for anything commercial breaches the terms, and "it was only a prototype" is not
a defence anyone has enjoyed making. Note also that free tiers are commonly
size-limited rather than time-limited, which means your model will work fine
until it grows.

**And the open-source ones have none of this.** No licence server, no tokens, no
node locking, no phone call when you scale to forty workers. `pip install
highspy` and it runs. That is not a small advantage, and it is regularly the
deciding one for a team that would otherwise be slightly better served by a
commercial solver.

The practical rule: **decide how you will deploy before you decide what to
deploy.** Solver choice is easy to reverse behind a modelling layer. A licensing
model that does not fit your infrastructure is not.

> **In one sentence.** Pick the licence type your deployment can live with
> first, because that constraint is harder to change than the solver.

---

Chapter 13 of 14

Previous: [Measure on your own models](../12-measure-your-own/README.md)  
Next: [How to choose](../14-how-to-choose/README.md)  
Contents: [solvers](../../README.md)
