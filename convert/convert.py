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
import copy
import sys

    

class UnitOfMeasurement:
    def __init__(self, scale=1, dimensions={}):
        self.scale = scale
        self.dimensions = dimensions
     
    
    def __mul__(self, x):
        result = UnitOfMeasurement(self.scale * x.scale)
        result.dimensions = dict( (n, self.dimensions.get(n, 0)+x.dimensions.get(n, 0)) 
                                  for n in set(self.dimensions)|set(x.dimensions) )
        return result
            
            
    def __div__(self, x):
        result = UnitOfMeasurement(self.scale / x.scale)
        result.dimensions = dict( (n, self.dimensions.get(n, 0)-x.dimensions.get(n, 0)) 
                                  for n in set(self.dimensions)|set(x.dimensions) )
        return result
    
    def __eq__(self, x):
        return self.scale == x.scale and self.dimensions == self.dimensions
    
    def __str__(self):
        return "< scale = " + self.scale + " dimensions = " +  self.dimensions +" >"

    def isCompatible(self, x):
        return self.dimensions == x.dimensions
    
    def dimensionsString(self):
        abbrev = [k for k, v in knownDimensions.iteritems() if v == self.dimensions]
        if len(abbrev) == 1:
            return abbrev[0]
        else:
            return str(self.dimensions)
        
    def conversionFactor(self, dest):
        return self.scale / dest.scale
    
  
  
def unitFromToken(token):
    unit = getBaseUnit(token.baseUnit)
    
    if token.prefix:
        unit.scale *= knownPrefix[token.prefix]
    
    if token.exp:
        for k in unit.dimensions.keys():
            unit.dimensions[k] *= token.exp

        unit.scale = unit.scale ** token.exp  
    return unit

  
def unitFromExpr(expr):
    result = unitFromToken(expr[0])
    tokens = iter(expr[1:])
    for operator, unitToken in izip(tokens, tokens):
        result = knownOperators[operator]( result,  unitFromToken(unitToken) )
        
    return result


knownBaseUnits  = {'1': UnitOfMeasurement(1.0, {}),
                   'm': UnitOfMeasurement(1.0, {'L': 1}),
                   'mm': UnitOfMeasurement(0.001, {'L': 1}),
                   'mi': UnitOfMeasurement(1609.344, {'L': 1}),
                   'ft': UnitOfMeasurement(0.3048, {'L': 1}),
                   's': UnitOfMeasurement(1.0, {'T': 1}),
                   'h': UnitOfMeasurement(3600.0, {'T': 1}),
                   'Hz': UnitOfMeasurement(1.0, {'T': -1}),
                   'g': UnitOfMeasurement(1.0, {'M': 1}),
                   'lb': UnitOfMeasurement(453.59237, {'M': 1}),
                   'oz': UnitOfMeasurement(28.3495231, {'M': 1}),
                   'l': UnitOfMeasurement(0.001, {'L': 3}),
                   'gal': UnitOfMeasurement(0.00378541178, {'L': 3}),
                   'N': UnitOfMeasurement(0.001, {'M': 1, 'L': 1, 'T': -2}),
                   'usd': UnitOfMeasurement(1, {'V': 1}),
                   'eur': UnitOfMeasurement(1.3662, {'V': 1})
                   }

def getBaseUnit(name):
    return copy.deepcopy(knownBaseUnits[name])


knownDimensions = {'length': {'L':1},
                   'area': {'L':2},
                   'volume': {'L':3},
                   'time': {'T': 1},
                   'weigth': {'M': 1},
                   'speed': {'T': -1, 'L':1}, 
                   'acceleration': {'T': -2, 'L':1} 
                   }


knownPrefix = {'p': 10**-12,
               'n': 10**-9,
               'u': 10**-6,
               'd': 10**-1,
               'c': 10**-2,
               'm': 10**-3,
               'k': 10**3,
               'M': 10**6,
               'G': 10**9,
               'T': 10**12,
               }

knownOperators = {'*': lambda x,y: x * y, 
                  '/': lambda x,y: x / y,  
                  }
    
def findKey(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val][0]



def parseInput(string): 
    
    valueExpr = Word(nums + "." + "+" + "-" + "*" + "/" + "(" + ")" ).setResultsName("valueExpr")
    prefix = oneOf( " ".join(knownPrefix.keys()) ).setResultsName("prefix")
    baseUnit = oneOf( " ".join(knownBaseUnits.keys()) ).setResultsName("baseUnit")
    exp = Word(nums).setResultsName("exp").setParseAction(lambda tokens: int(tokens[0]))
    unitAtom = Combine( ( baseUnit | prefix + baseUnit) + Optional(Optional("^") + exp) ).setResultsName("unit")
    operator = oneOf(" ".join(knownOperators.keys()) ).setResultsName("operator")
    unitExpr = Group( unitAtom + ZeroOrMore(operator + unitAtom) )
    input = valueExpr + unitExpr("srcExpr") + "to" + unitExpr("dstExpr")
    
    return input.parseString(string, parseAll=True)
   

class ConversionResult:
    def __init__(self):
        self.__src = None
        
        
def convert(value, srcUnit, dstUnit):    
    if not srcUnit.isCompatible(dstUnit):
        raise RuntimeError("Incompatible type " + srcUnit.dimensionsString() + " and " + dstUnit.dimensionsString() )
    
    return value * srcUnit.conversionFactor(dstUnit)


def convertString(string):
    res = parseInput(string) 
    srcUnit = unitFromExpr(res.srcExpr)
    dstUnit = unitFromExpr(res.dstExpr)
    try:
        value = eval(res.valueExpr)
    except:
        raise RuntimeError(res.valueExpr + ' is not a valid value')
    return convert(value, srcUnit, dstUnit)


if __name__ == "__main__":
    args = " ".join(sys.argv[1:])
    try:
        print convertString(args)
    except Exception, e:
        print e
    