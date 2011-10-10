# module convert.py
#
# Copyright (c) 2011  Andrea Grandi
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from pyparsing import *
from itertools import izip


class UnitsOfMeasurement:
    def __init__(self, scale=1, dimensions=[]):
        self.scale = scale
        self.dimensions = dimensions
     
    
    def __mul__(self, x):
        return UnitsOfMeasurement(self.scale * x.scale)
    
    def __div__(self, x):
        return UnitsOfMeasurement(self.scale / x.scale)
    
    def __string__(self):
        return "< scale = " + self.scale + " >"
    

def unitFromToken(token):
    print token
    print token.prefix
    unit = UnitsOfMeasurement()
    unit.scale = 1.343
    unit.dimensions.append("T")
    return unit


def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

def unitFromExpr(expr):
    result = unitFromToken(expr[0])
    for operator, token in pairwise(expr[1:]):
        if operator == "*":
            result *= unitFromToken(token)
        else:
            result /= unitFromToken(token)
        
    return result


def parseInput(string): 
    
    value = Word(nums).setResultsName("value").setParseAction(lambda tokens: int(tokens[0]))
    prefix = oneOf("p n u m d h k M G T").setResultsName("prefix")
    baseUnit = oneOf("m s h l mi in g N").setResultsName("baseUnit")
    unitAtom = Combine( ( baseUnit | prefix + baseUnit) + Optional(Word(nums).setResultsName("exp")) ).setResultsName("unit")
    operator = oneOf("* /").setResultsName("operator")
    unitExpr = Group( unitAtom + ZeroOrMore(operator + unitAtom) )
    input = value + unitExpr("srcExpr") + "to" + unitExpr("dstExpr")
    
    return input.parseString(string, parseAll=True)
    
    
def parseUnitOfMeasurement(string):
    raise NotImplementedError
    