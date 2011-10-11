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
    def __init__(self, scale=1, dimensions={}):
        self.scale = scale
        self.dimensions = dimensions
     
    
    def __mul__(self, x):
        result = UnitsOfMeasurement(self.scale * x.scale)
        result.dimensions = dict( (n, self.dimensions.get(n, 0)+x.dimensions.get(n, 0)) 
                                  for n in set(self.dimensions)|set(x.dimensions) )
        return result
            
            
    def __div__(self, x):
        result = UnitsOfMeasurement(self.scale / x.scale)
        result.dimensions = dict( (n, self.dimensions.get(n, 0)-x.dimensions.get(n, 0)) 
                                  for n in set(self.dimensions)|set(x.dimensions) )
        return result
    
    
    def __string__(self):
        return "< scale = " + self.scale + " dimensions = " +  self.dimensions +" >"




knownBaseUnits  = {'m': UnitsOfMeasurement(1, {'L': 1}),
                  'mi': UnitsOfMeasurement(1609.344, {'L': 1}),
                  's': UnitsOfMeasurement(1, {'T': 1}),
                  'h': UnitsOfMeasurement(3600, {'T': 1}),
                  'g': UnitsOfMeasurement(1, {'M': 1}),
                  'lb': UnitsOfMeasurement(453.59237, {'M': 1}),
                  'l': UnitsOfMeasurement(0.001, {'L': 3}),
                  'N': UnitsOfMeasurement(0.001, {'M': 1, 'L': 1, 'T': -2})
                  }


knownDimensions = {'length': {'L':1},
                   'area': {'L':2},
                   'volume': {'L':3},
                   'time': {'T': 1},
                   'mass': {'M': 1},
                   'speed': {'T': -1, 'L':1}, 
                   'acceleration': {'T': -2, 'L':1} 
                   }


knownPrefix = {'p': 10**-12,
               'n': 10**-9,
               'u': 10**-6,
               'm': 10**-3,
               'k': 10**3,
               'M': 10**6,
               'G': 10**9,
               'T': 10**12,
               }
    
def findKey(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val][0]


def parseInput(string): 
    
    value = Word(nums).setResultsName("value").setParseAction(lambda tokens: int(tokens[0]))
    prefix = oneOf("p n u m d h k M G T").setResultsName("prefix")
    baseUnit = oneOf("m s h l mi in g N").setResultsName("baseUnit")
    exp = Word(nums).setResultsName("exp").setParseAction(lambda tokens: int(tokens[0]))
    unitAtom = Combine( ( baseUnit | prefix + baseUnit) + Optional(exp) ).setResultsName("unit")
    operator = oneOf("* /").setResultsName("operator")
    unitExpr = Group( unitAtom + ZeroOrMore(operator + unitAtom) )
    input = value + unitExpr("srcExpr") + "to" + unitExpr("dstExpr")
    
    return input.parseString(string, parseAll=True)
    
    
def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)
 

def unitFromToken(token):
    unit = knownBaseUnits[token.baseUnit]
    
    if token.prefix:
        unit.scale *= knownPrefix[token.prefix]
    
    if token.exp:
        for k in unit.dimensions.keys():
            unit.dimensions[k] *= token.exp

        unit.scale = unit.scale ** token.exp  
        
    return unit


def unitFromExpr(expr):
    result = unitFromToken(expr[0])
    for operator, token in pairwise(expr[1:]):
        if operator == "*":
            result *= unitFromToken(token)
        else:
            result /= unitFromToken(token)
        
    return result
    