<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 0 · What this is

![A scale marked in boards. A grey bar creeps up to five point four four, then a
blue bar pushes past six to six and a half, and the answer lands on
seven.](hero.gif)

Boards come 25 feet long. Today's order is three pieces of 4 feet, six pieces
of 9 feet and seven pieces of 10 feet. You may cut each board however you like,
cutting is free, and whatever is left at the end of a board is scrap — two
offcuts cannot be glued back together. **How few boards can fill the order?**

The answer is seven. The interesting part is not the seven; it is that
establishing it takes two separate pieces of work, and only one of them is easy.

Showing that seven is *enough* is the easy half. Cut seven boards in some
sensible way, lay out the pieces, and count. Anyone can check it. But that only
shows seven works — on its own it leaves open that some cleverer arrangement
does the job in six.

Ruling out six is the hard half, and you cannot get there by trying
arrangements, because there are far too many to try. You need an argument that
covers every arrangement at once, including the ones nobody thought of. Here
are two such arguments. Both are correct. Only one is any use.

**First argument: count the wood.** The order asks for
3×4 + 6×9 + 7×10 = 136 feet of wood, and each board supplies 25 feet. Even if
not one inch were wasted, 136 ÷ 25 = 5.44 boards' worth of wood is needed, so
five boards cannot possibly be enough. At least six.

**Second argument: count the long pieces.** Call a piece **long** if it is 9
feet or 10. The three shortest long pieces together are 9 + 9 + 9 = 27 feet,
and a board is 25, so no board can carry three long pieces — two is the most
any board can hold, however it is cut. The order asks for 6 + 7 = 13 long
pieces. At two to a board, 13 ÷ 2 = 6.5 boards are needed, and you cannot buy
half a board. At least seven.

That second argument settles it. At least seven, and seven can be cut, so seven
is the answer and the question is closed. It took twenty seconds and you
checked it yourself.

Now the point of the guide. Both arguments are lower limits on the number of
boards, both were obtained by ignoring some of what makes the problem hard, and
one of them is worth 1.06 boards more than the other. When people say a way of
writing down a problem is *stronger*, this is the entire meaning: it produces
limits closer to the truth, and a limit closer to the truth is what lets you
stop searching sooner.

The catch is that nobody hands you the second argument. It came from noticing
something about this particular order, and a real order has hundreds of
lengths, where nothing will be noticeable. What is needed is a procedure that
manufactures arguments of that quality automatically. There is one. Its cost is
that it works with one unknown for every way of cutting a single board that is
worth using at all — six of them for this order, and roughly four trillion for a
paper mill.

> **In one sentence.** Finding a good answer is easy and proving nothing beats
> it is hard, and how well you can prove it depends entirely on how the question
> was written down.

---

Chapter 0 of 11

Next: [The order](../01-the-order/README.md)  
Contents: [branch-and-price](../../README.md)
