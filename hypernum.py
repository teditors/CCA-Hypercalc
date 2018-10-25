# -*- coding: utf-8 -*-
"""
Created on Nov 2 2017

@author: Andrew Northrup

Hypernum class represents a number as a 2 mpmath mpfloats and 1 int:
m       mantissa        mpf
e       exponent        mpf
PT      power tower     int

representing ((10**)*PT)**(m*10**e)

This design owes a great deal to hypercalc.pl by Robert P. Munafo, see:
https://mrob.com/pub/comp/hypercalc/hypercalc-javascript.html

This only works for positive whole numbers, very limited functionality.
Enough for chain arrow calculations.
"""
from hn_utils import addlog, sublog, biggest_first
from mpmath import mp, mpf, floor, log10, power
mp.dps = 100 # mpf decimal precision

class hypernum(object):

    max_int = 10000
    max_exp = 2000.0 # threshold exponential value, ensures safe conversion to mpf
    max_PT = 8 # after which display xPT instead of "10^"*x

    def __init__(self, m = '0.0', e = '0.0', pt = '0'):
        if type(m) == hypernum:
            self.m = m.m
            self.e = m.e
            self.PT = m.PT
        else:
            self.m = mpf(str(m)) # mantissa
            self.e = mpf(str(e)) # exponent
            self.PT = int(pt) # "power tower" of 10s counter
        self.normalize()

    def __repr__(self):
        s = ""
        if self.PT < self.max_PT:
            for i in range(self.PT):
                s = s + "10^"
        else:
            s = s + str(self.PT) + "PT^"
        if self.e < mpf('10'):
            tmp = self.m*power(10, self.e)
            s = s + str(tmp)
        else:
            s = s + str(self.m)
            s = s + "e" + str(self.e)
        return s

    #GT/LL/EQ function overloads
    def __gt__(self, other):
        if self.PT > other.PT:
            return True
        elif self.PT < other.PT:
            return False
        else:
            if self.e > other.e:
                return True
            elif self.e < other.e:
                return False
            else:
                return self.m > other.m

    def __eq__(self, other):
        x=False
        if self.PT == other.PT:
            if self.e == other.e:
                if self.m == other.m:
                    x = True
        return x

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return other > self

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not self == other

    # + addition function overload
    def __add__(self, other):
        x, y = biggest_first(self, other)
        if x.PT == 0:
            m = x.mpf() + y.mpf()
            return hypernum(m, 0, 0)
        elif x.PT == 1:
            if y.PT == 0:
                m = addlog(x.mpf(), log10(y.mpf()))
            else: # y.pt == 1
                m = addlog(x.mpf(), y.mpf())
            return hypernum(m, 0, 1)
        else: # "power tower paradox": addition of PT > 1 numbers is futile
            return x # just return largest

    # Note that self is always > other in our cca implementation.
    # need to deal with all cases to make generally useful
    # also need to deal with possibility of negative numbers
    def __sub__(self, other):
        self.normalize()
        if self.PT == 0:
            m = self.mpf() - other.mpf()
            return hypernum(m, 0, 0)
        elif self.PT == 1:
            if other.PT == 0:
                m = sublog(self.mpf(), log10(other.mpf()))
            else: # other.pt == 1
                m = sublog(self.mpf(), other.mpf())
            return hypernum(m, 0, 1)
        else: # numbers too big, abandon all hope
            return self # just return largest

    # * multiplication function overload
    def __mul__(self, other):
        x, y = biggest_first(self, other)
        if x.PT==0:
            m = x.mpf() * y.mpf() # should be safe
            return hypernum(m, 0, 0)
        elif x.PT == 1:
            if y.PT == 0:
                m = x.mpf() + log10(y.m) + y.e
            else:
                m = m = x.mpf() * y.mpf()
            return hypernum(m, 0, 1)
        elif x.PT == 2 and y.PT == 2:
            m = addlog(x, y)
            return hypernum(m, 0, 2)
        else:
            return x # "power tower paradox"

    # turn hypernum to mpf to use mpf functions I don't want to/can't rewrite
    # NOTE: ignores PT term!!!
    # Also may blow up if using large exponent term, its not magic
    def mpf(self):
        return mpf(self.m*(10**self.e))

    # ** power function overload
    def __pow__(self, power, modulo=None):
        if self.e == 0 and power.e == 0:
            tmp = self.m ** power.m
            return hypernum(tmp, 0, self.PT)
        else:
            tmp = self.log10()*power
            tmp = tmp.antilog10()
            return hypernum(tmp.m, tmp.e, tmp.PT) # use constructor to normalize

    # base 10 log function - easy
    def log10(self):
        if self.PT == 0:
            return hypernum((log10(self.m)+self.e))
        else:
            return hypernum(self.m, self.e, (self.PT-1))

    # 10**x function (antilog)
    def antilog10(self):
        return hypernum(self.m, self.e, (self.PT+1))

    # VERY IMPORTANT normalize routine
    # Ensures conistant format, no overuns (of m or e)
    def normalize(self):
        if self.e == 0 and self.PT > 0:
            self.PT = self.PT -1
            self.m = power(10, self.m)
        e=floor(log10(self.m))
        self.e += e
        self.m *= power(10, -e)
        while self.e > self.max_exp:
            self.m = self.e + log10(self.m)
            e = floor(log10(self.m))
            self.e = e
            self.m *= power(10, -e)
            self.PT += 1

if __name__ == '__main__':

    def test(a, b='0.0', c='0'):
        x = hypernum(a, b, c)
        print(x)

    test('1.340780793e+154', '0.0', '0')
    test(hypernum(0.9, 8, 1))