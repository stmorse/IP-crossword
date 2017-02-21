# IP-crossword

The `ipxword.py` script in this repo is a crossword compiler using integer optimization (IO/IP).  Crossword as in dense newspaper-style crossword.  I believe the usual way crossword makers attack this problem is with "[constraint satisfaction programming](http://ai.stanford.edu/~jduchi/projects/crossword_writeup.pdf)" (CSP) methods (for example, I'm pretty sure CSP is what the commercial, Windows-only [Crossword Compiler](http://www.crossword-compiler.com) uses, which is the industry standard).  So I'm trying to do something different with the IP way, although it has been discussed before.   

Details on the methodology in a [blog post over here](https://stmorse.github.io/journal/IP-Crossword-puzzles.html).

## Usage

The bones of the `ipxword.py` script are (1) a `Grid` class which wraps convenience methods for manipulating the crossword grid, and (2) a `IPXWordGenerator` class which takes a `Grid` as input and formulates and solves as an integer optimization problem (IO/IP).   

Assuming you have Python installed, to try it out, first clone this repository
```
$ git clone https://github.com/stmorse/IP-crossword.git
```
and make sure you have the `PuLP` package installed (the only dependency) by running
```
$ pip install pulp
```
Then you can create a simple 3x3 test grid by just running
```
$ python ipxword.py
```
which should print out something like
```
you/IP-crossword $ python ipxword.py
GRID:
# - - 
- - - 
- - - 

Number slots: 6
Different word lengths possible: {2, 3}
Dictionary size after sampling: 500
(Using random word values.)

Building...
Puzzle status: Optimal

Total words: 6
Assignments: (index, (slot), word)
(19, (2, 'across'), 'ems')
(33, (0, 'across'), 'ma')
(207, (1, 'down'), 'mum')
(227, (2, 'down'), 'ars')
(323, (0, 'down'), 'pe')
(379, (1, 'across'), 'pur')
```
Like I said, the `ospd.txt` wordlist is pretty crummy.

You can also play around with it a little more in an IPython notebook, if you prefer.  The `Grid` class takes a size parameter and a list of where you want the black squares to be (list of coordinate tuples).  Right now I've only had success getting the default solver to handle grids with `N=3` or `N=4`, and only taking a sample of `numk=500` words or so.

## To Do

**This is a Work-In-Progress**, (but it is working).  I think the following improvements may help:

1. Improve the grid handling --- currently very hacky, using base Python, lots of list comprehensions and loops ... blech.
2. Use something better than the default solver for `PuLP`.  
3. Related: a better solver might be able to give insight if there are pre-processing steps that speed things up.
4. Improve the word list and add points per word.  Most of a crossword maker's struggle (I'm told) is getting a good, well-sorted word list.  Currently I'm using a `ospd.txt` file with a few thousand words, most of which are crummy/archaic, and assigning each word a random score. 

Also, crossword constructors typically want to be able to specify certain word-to-slot assignments, and/or specify certain words they want to ensure make it in the grid.  This code already has the bones to handle this, and it wouldn't take much to fill out the `set_words()` method in `IPXWordGenerator` to handle these kinds of constraints.  The idea is:

1. To specify a word-to-slot assignment, simply set the corresponding decision variable `zvars[k,s] = 1` where `k` corresponds to the word index you want and `s` corresponds to the slot assignment.
2. To specify a word-in-the-puzzle assignment, you could do one of two things:  (1) either give that word a very high associated cost by adjusting `allcosts[k]`.  OR, (2) specify a new constraint that `LpSum(zvars[k,s] for s in slots) == 1`, i.e. that word `k` must be assigned to exactly one of the slots in the puzzle.

Again, check out [my post](https://stmorse.github.io/journal/IP-Crossword-puzzles.html) to get a better feel for the underlying math of the algorithm.

Enjoy!

Feel free to send me comments on [Twitter](https://twitter.com/thestevemo).
