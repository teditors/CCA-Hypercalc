# -*- coding: utf-8 -*-
"""
Created on Nov 2 2017

@author: Andrew Northrup

Utility module for hypernum

This design owes a great deal to hypercalc.pl by Robert P. Munafo, see:
https://mrob.com/pub/comp/hypercalc/hypercalc-javascript.html
"""
from mpmath import mp, mpf, floor, log10, power

# Makes sure hypernum x is bigger than y, switches if not
def biggest_first(x, y):
    if x < y:  # ensure x is larger
        t = x
        x = y
        y = t
    return x, y

# Addlog function: used for adding PT == 1 hns, multiplying PT == 2 hns
def addlog(x, y):
    x, y = biggest_first(x, y)
    tmp = y.mpf() - x.mpf()
    tmp = 1 + 10**tmp
    return x + log10(tmp)

# Sublog function, see above
# We only ever subtract 1 in cca.py, so this could be simpler, but
# its easy once addlog is developed so why not?
def sublog(x,y):
    x, y = biggest_first(x, y)
    tmp = y - x
    tmp = 1 - 10**tmp
    return x + log10(tmp)