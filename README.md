# Lazor-Project-G2

"Lazors" is a puzzle game available on Android and iPhone. The player (you!) places blocks on the board to guide the laser beam to hit specific targets by placing blocks with special functions: block, reflection, refraction, and transparent.

The free version of the game provides only three hints. So, are you stuck with a problematic board? You don't have any free hints left? No way you can solve the puzzle on your own? It's okay—we've got you!



### ⚙️How to use:

When you cannot solve a particular board, make your .bff file and use "[our code file name]" to solve it.

The .bff file needs to start with the board structure you want to solve. Write down the board between the GRID START and the GRID STOP. For example:

```
GRID START
o B x o o
o o o o o
o x o o o
o x o o x
o o x x o
B o x o o
GRID STOP
```

Each block needs to be represented with x for no blocks allowed, o for blocks allowed, A for reflect block, B for opaque block, and C for refract block. In the board representation, include all the fixed blocks!

The horizontal direction is the x-axis (right for +ve), and the vertical direction is the y-axis (down for +ve).

Next, we specify the number of blocks we have. For example:

```
A 8
```

Use the same notation as the board representation (A, B, and C).

Now, we need to have a laser to solve the laser game. The lazor is denoted as L in the .bff file with two numbers representing start coordinates followed by two numbers representing the direction. For example:

```
L 4 1 1 1
```

Lastly, the .bff file should contain the coordinates of the point at which the laser needs to intersect. In the Lazor game, it will be a circle at the border of the block. For example:

```
P 6 9
P 9 2
```

After compiling all the necessary parts into the .bff file, **voila!** You are ready to get the solution!

*We used yarn_5.bff as an example of structuring the .bff file. Check the file if you are unsure how to compile all the necessary parts!*



### 🎉What you will get:

Unless the board is super complicated or big, the solution will be given within [TIME TAKEN]. The code will provide [POSSIBLY THE OUTPUT FILE NAME]. Open it, use it, and the puzzle is solved!



### 📧Still confused? Contact us!
Nithya Parthasarathi (nparthasarathi17 | npartha2@jh.edu)
+ Identified the logic and initiated the code generation
 
Clara Hyeonji Kim (clarahjk00 | hkim348@jh.edu)
+ README.md 
