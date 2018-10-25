# -*- coding: utf-8 -*-
"""
Created on Nov 15 2017

@author: Andrew Northrup

simple CCA calculator Front End
Gratuitous use of re and try/except to fulfill project requirements
"""

from cca import cca
import re

class NanError(Exception):
    def __str__(self):
        return "is not a positive whole number"

class TooManyTerms(Exception):
    def __str__(self):
        return "Too many terms.  Please enter 2-4 terms."

class TooFewTerms(Exception):
    def __str__(self):
        return "Too few terms.  Please enter 2-4 terms."

def verifyPWN(r):
    if r is None:
        raise NanError

def verifylength(l):
    if len(l) < 2:
        raise TooFewTerms
    elif len(l) > 4:
        raise TooManyTerms

number_check = re.compile(r'\d+')
cont = True
while cont == True:
    valid_in = True
    cca_string = input("Enter a CCA, 2-4 positive whole numbers separated by right angle bracket /'>/': ")
    cca_list = cca_string.strip().split('>')
    try:
        verifylength(cca_list)
    except TooFewTerms as f:
        print(f)
        valid_in = False
    except TooManyTerms as m:
        print(m)
        valid_in = False
    for item in cca_list:
        try:
            r = number_check.search(item)
            verifyPWN(r)
        except NanError as n:
            print(item, n)
            valid_in = False
    if valid_in:
        c = cca(cca_list, False)
        print('input CCA: ', c)
        c.applyrules()
        print('reduced expression: ', c)
    cont_str = input("Continue Y/N?")
    if cont_str == ('n' or 'N'):
        cont = False