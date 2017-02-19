# IP-crossword

The `ip.pynb` notebook in this repo is a crossword compiler using integer optimization (IO/IP).  Crossword as in dense newspaper-style crossword.  I believe the usual way crossword makers attack this problem is with "[constraint satisfaction programming](http://ai.stanford.edu/~jduchi/projects/crossword_writeup.pdf)" (CSP) methods (for example, I'm pretty sure CSP is what the commercial, Windows-only [Crossword Compiler](http://www.crossword-compiler.com) uses, which is the industry standard).  So I'm trying to do something different with the IP way, although it has been discussed before (e.g. the paper included in the repo).   

More details on the methodology forthcoming in a [blog post over here](http://stmorse.github.io), stay tuned...  

The bones of the notebook are (1) a `Grid` class which wraps convenience methods for manipulating the crossword grid, and (2) a chunk of code which formulates and solves as an integer optimization problem (IO/IP).   

**This is a WIP** (but it is working).  It doesn't appear able to handle puzzles beyond 10-16 squares right now, but I think the following improvements may help:

1. Improve the grid handling --- currently very hacky, using base Python, lots of list comprehensions and loops ... blech.
2. Use something better than the default solver for `PuLP`.  
3. Related: a better solver might be able to give insight if there are pre-processing steps that speed things up.
4. Improve the word list and add points per word.  Most of a crossword maker's struggle (I'm told) is getting a good, well-sorted word list.  Currently I'm using a `ospd.txt` file with a few thousand words, most of which are crummy/archaic, and assigning each word a random score.   

Feel free to send me comments on [Twitter](https://twitter.com/thestevemo).
