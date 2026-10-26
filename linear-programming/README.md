# Linear programming

*Corners, walls and prices.*

Linear programming from one small farm (20 acres, 32 units of water, wheat or
corn), following Craig Tovey's *Linear Optimization and Duality*, chapters 1–8.
Written for a reader with no background. In progress: chapters 0–2.

**[Read it as one page →](https://bayzhan8.github.io/Illuminate/linear-programming/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/linear-programming/sandbox/)**

| | | |
|---|---|---|
| 0 | [What this is](https://bayzhan8.github.io/Illuminate/linear-programming/#ch0) | the simplex walk, as a promise |
| 1 | [A plan inside the walls](https://bayzhan8.github.io/Illuminate/linear-programming/#ch1) | plans are points, resources are walls |
| 2 | [The best plan sits on a corner](https://bayzhan8.github.io/Illuminate/linear-programming/#ch2) | all corn earns $80,000; the corner earns $84,000 |

Every number is computed in exact fractions by `src/linprog/`. Tests check the
maths two independent ways (simplex vs corner enumeration, prices vs the dual
solved fresh), the prose against the code, and the sandbox JavaScript against
the Python.

```bash
cd .. && make bootstrap   # once
cd linear-programming
make check                # render, publish, verify
```
