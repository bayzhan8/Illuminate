<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · The price is only local

Keep adding planks and eventually the saw becomes the problem instead. From
that point on, extra planks pile up unused and are worth nothing.

![The workshop's best profit as a function of how many planks it has: three
straight pieces, each flatter than the last, bending at twenty planks and at
just over forty five.](curve.png)

The whole curve is three straight pieces, and the plank price is *the slope of
the piece you happen to be standing on*:

| planks in stock | one more plank is worth | why |
|---|---|---|
| under 20 | $10.00 | so few planks that tables are not worth building at all |
| 20 to 45 ⅐ | **$6.25** | where this workshop actually is |
| over 45 ⅐ | $0.00 | the saw is the binding rule now; planks pile up |

Both bends have a reason, and the odd-looking one has the better reason.

**The first bend, at 20 planks.** Compare the two products by what they get out
of a plank. A chair uses 2 planks and earns $20, which is $10 a plank. A table
uses 4 planks and earns $30, which is $7.50. So while planks are the only thing
running out, the workshop should build chairs and nothing else, and every extra
plank is half a chair, worth $10. That lasts until the chairs run into a
different shelf. Ten chairs take 30 hours of work, and 30 hours is all there
is; ten chairs also take exactly 20 planks. Twenty planks is the point where
the hours run out and the cheap ride ends.

**The second bend, at 45 ⅐ planks.** Past 20 planks, extra planks have to buy
their way in through the trade from chapter 7: eight planks in, three tables up,
two chairs down. That trade leaves the hours alone. It does not leave the saw
alone. Three more tables want 9 hours of saw time, two fewer chairs give back
2, so every swap of eight planks eats 7 hours of saw time.

The workshop has 1 hour of saw time spare, the one from chapter 6. One spare
hour against 7 per swap buys one seventh of a swap, and one seventh of eight
planks is 1 ⅐ planks. That is the whole of the ⅐. It is one spare saw-hour
divided by the seven the trade consumes. After that the saw is empty, no
further tables can be built, and arriving planks have nowhere to go.

The workshop has 44 planks. It is 1 ⅐ planks away from its price collapsing to
nothing.

That is a narrow shelf to be standing on, and it is the most common way this
idea gets misused. A shadow price quoted without the range over which it holds
is close to useless.

The pieces get flatter, never steeper. Easy uses go first, so more of a
resource is never worth more per unit than the last lot was, and the curve can
only bend one way.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/08.html)**
Slide the stock of any of the three resources and watch its own price step down.

> **In one sentence.** A shadow price is a local slope with an expiry date, so
> it always has to be quoted with the range over which it holds.

---

Chapter 8 of 10

Previous: [What one more plank is worth](../07-what-one-more-is-worth/README.md)  
Next: [When it goes wrong](../09-when-it-goes-wrong/README.md)  
Contents: [lp-duality](../../README.md)
