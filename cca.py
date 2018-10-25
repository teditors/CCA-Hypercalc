# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 2017

@author: Andrew Northrup

Conway Chain Arrow class, see:
https://sites.google.com/site/pointlesslargenumberstuff/home/2/chainarrows
https://en.wikipedia.org/wiki/Conway_chained_arrow_notation

Rules for reduction (per first link, there are equivalent alternatives):

Each chain can only be evaluated to a number by reducing it to 2 terms (A > B),
which evaluates as A**B. (Rule 1)

Any '1' can be removed, along with any terms to the right (rules 2 & 3)

(A > B > C ) == ( A > (A > B-1 > C) > C-1)  (Rule 4)

CCAs are reduced by expanding by rule 4 until 1's are produced, hacking them off, repeat
until a CCA is 2 terms, then evaluating numerically.  It would be nice to evaluate 3 term CCAs directly,
but hyperoperations 4+ are not well-defined or numerically well-behaved

CCA is composed of class hypernums and class CCAs
"""
from mpmath import mpf, mp, floor, log10
from sys import setrecursionlimit
import hypernum as hn

setrecursionlimit(4000) # be careful to avoid overflow
mp.dps = 8
max_expandable = hn.hypernum('1000')

class cca(object):  # variable chain arrow of n terms (beware overruns)

    def __init__(self, a=[], verbose=False, runaway=False, reduced=False, whole=None):
        self.reduced = reduced  # True means stop reduction and go home
        self.verbose = verbose  # give debug info
        self.original = a  # in case reduction is going poorly, return orginal (unused)
        self.runaway = runaway  # further reduction is not fruitful
        self.a = []
        for i in range(len(a)):
            if type(a[i]) == hn.hypernum:
                self.a.append(a[i])
            else:
                tmp = hn.hypernum(str(a[i]))
                self.a.append(tmp)
        if whole == None:
            whole = self
        self.whole = whole

    # print complete cca, nested terms too
    def __repr__(self):  # pass s by ref
        s = "( "
        for i in range(len(self.a) - 1):
            if type(self.a[i]) == cca:
                s = s + repr(self.a[i])
                s = s + " > "
            else: # is hypernum
                s = s + "%s" % self.a[i]
                s = s + " > "
        s = s + "%s )" % self.a[-1]
        return s

    def __str__(self):
        return repr(self)

    # Casts a CCA to a hypernum
    # USE ONLY ON 1 TERM CCAs
    @staticmethod
    def tonum(x):
        if type(x) == cca:
            return hn.hypernum(x.a[0])
        else:
            return x

    # A couple of shortcuts
    def rule0(self):
        if len(self.a) > 1:
            if type(self.a[0]) == hn.hypernum and type(self.a[1]) == hn.hypernum:
                if self.a[0] == self.a[1] == hn.hypernum(2):
                    self.a = [hn.hypernum(4)]
                    self.reduced = True
                elif self.a[0] == hn.hypernum(1):
                    self.a = [hn.hypernum(1)]
                    self.reduced = True
            if (self.verbose and self.reduced):
                print("Rule 0")
                print(self.a)

    def rule1(self):
        if (len(self.a) < 3):
            self.reduced = True
            if self.verbose:
                print("rule 1: ")
                print(self.whole)
        if (len(self.a) == 2):
            tmp = self.tonum(self.a[1])
            self.a[0] = self.tonum(self.a[0] ** tmp)
            self.a.pop(1)
            if self.verbose:
                print(self.a)

    def rule2(self):
        if type(self.a[-1]) == hn.hypernum:
            if (self.a[-1] == hn.hypernum(1)):
                self.a.pop(-1)
                if self.verbose == True:
                    print("rule 2: ")
                    print("self = ", self.whole)

    def rule3(self):
        if type(self.a[-2]) == hn.hypernum:
            if (self.a[-2] == hn.hypernum(1)):
                self.a.pop(-1)
                self.a.pop(-1)
                if self.verbose == True:
                    print("rule 3: ")
                    print("self = ", self.whole)

    def rule4(self):
        b = self.tonum(self.a.pop(-1))
        a = self.a.pop(-1)
        a = self.tonum(a)
        a = a - hn.hypernum("1")
        inner = cca(a=self.a, verbose=self.verbose, whole=self.whole)
        inner.a.extend([a, b])
        if (type(b) == cca):
            b = self.tonum(b)
        self.a.extend([inner, b - hn.hypernum("1")])
        if self.verbose:
            print("rule 4: ")
            print("self = ", self.whole)
        inner.applyrules() # recursive CCA reduction, works great

    # We don't want runaway recursion, this mostly prevents
    # (This problem is very difficult for the general case)
    def check4runaway(self):
        for i in range(len(self.a)):
            if type(self.a[i]) == cca:
                if (len(self.a[i].a) == 1):
                    self.a[i] = self.tonum(self.a[i])
                elif self.a[i].reduced:
                    self.runaway = True
            if type(self.a[i]) == hn.hypernum:
                if self.a[i] > max_expandable:
                    self.runaway = True

    # This is the reduction routine
    def applyrules(self):
        while not self.reduced:
            if self.runaway:
                self.reduced = True # done
            self.rule0()
            self.rule1()
            self.check4runaway() #if value too high for expansion
            if len(self.a) > 1:
                self.rule2()
            if len(self.a) > 2:
                self.rule3()
            if not (self.reduced or self.runaway):
                if len(self.a) > 2:
                    self.rule4()

# Tests
if __name__ == '__main__':
    def test(a=[]):
        x = cca(a, True)
        print(x)
        x.applyrules()
        print(x)


    #   Tests
    a = [2, 2, 3, 6, 99]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [3, 2, 3]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [2, 3, 3]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [3, 3, 2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [4, 3, 2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [3, 3, 2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [5, 3, 2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [5, 5, 2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [2, 3, 4]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [2, 3, 2, 2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [6,6,3]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [10,10,2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [100,100,2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [1000,1000,2]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [3, 3, 65]
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
    a = [3, 3, 65, 2] # > Graham's number!
    print("++++++++++++++++++++++++++++++++++++++++++++" + str(a) + "++++++++++++++++++++++++++++++++++++++++++++")
    test(a)
