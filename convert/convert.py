# Convert - Textual python unit converter
# Copyright (C) 2013  Andrea Grandi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import copy
import sys
from itertools import izip

from pyparsing import *
    

class UnitOfMeasurement:
    """Description of the unit of measurement

    It contains the information used to manipulate different units and perform the conversion.

    :param scale: multiplication factor used to convert the current UnitOfMeasurement to the base one
    :param dimensions: dimensions of the unit. It can be time, length, weight or a combination of the previous
    """
    def __init__(self, scale=1, dimensions={}):
        self.scale = scale
        self.dimensions = dimensions
     
    
    def __mul__(self, x):
        """Multiplication of two UnitOfMeasurement classes

        The results is a new UnitOfMeasurement where the scale is the product of the scales and the dimensions are the
        sums of the dimensions
        """
        result = UnitOfMeasurement(self.scale * x.scale)
        result.dimensions = dict( (n, self.dimensions.get(n, 0)+x.dimensions.get(n, 0)) 
                                  for n in set(self.dimensions)|set(x.dimensions) )
        return result
            
            
    def __div__(self, x):
        """Division of two UnitOfMeasurement classes

        The results is a new UnitOfMeasurement where the scale is the division of the scales and the dimensions are the
        differences of the dimensions
        """
        result = UnitOfMeasurement(self.scale / x.scale)
        result.dimensions = dict( (n, self.dimensions.get(n, 0)-x.dimensions.get(n, 0)) 
                                  for n in set(self.dimensions)|set(x.dimensions) )
        return result


    def __eq__(self, x):
        """Equality of two UnitOfMeasurement classes

        Two UnitOfMeasurement are equals if both the scale and the dimensions are the same
        """
        return self.scale == x.scale and self.dimensions == self.dimensions


    def isCompatible(self, x):
        """Compatibility of two UnitOfMeasurement classes

        Two UnitOfMeasurement are compatible if the dimensions are the same.
        The conversion between two UnitOfMeasurement can be done only if those are compatible.
        In other words, it's not possible to add meter (length) and seconds (time).
        """
        return self.dimensions == x.dimensions


    def conversionFactor(self, dest):
        """Conversion factor between used to convert the current UnitOfMeasurement to the destination
        """
        return self.scale / dest.scale


    def __str__(self):
        """String description of the UnitOfMeasurement
        """
        return "< scale = " + self.scale + " dimensions = " +  self.dimensions +" >"


    def dimensionsString(self):
        """String description of the dimensions
        """
        abbrev = [k for k, v in knownDimensions.iteritems() if v == self.dimensions]
        if len(abbrev) == 1:
            return abbrev[0]
        else:
            return str(self.dimensions)
        

#-------------------------------------------------------------

def unitFromToken(token):
    """Creates a UnitOfMeasurement from the given token"""
    unit = getBaseUnit(token.baseUnit)
    
    if token.prefix:
        unit.scale *= knownPrefix[token.prefix]
    
    if token.exp:
        for k in unit.dimensions.keys():
            unit.dimensions[k] *= token.exp

        unit.scale = unit.scale ** token.exp  
    return unit

  
def unitFromExpr(expr):
    """Creates a UnitOfMeasurement from the given expression"""
    result = unitFromToken(expr[0])
    tokens = iter(expr[1:])
    for operator, unitToken in izip(tokens, tokens):
        result = knownOperators[operator]( result,  unitFromToken(unitToken) )
        
    return result


#-------------------------------------------------------------

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


knownDimensions = {'length': {'L':1},
                   'area': {'L':2},
                   'volume': {'L':3},
                   'time': {'T': 1},
                   'weigth': {'M': 1},
                   'speed': {'T': -1, 'L':1},
                   'acceleration': {'T': -2, 'L':1}
                   }


# Prefix according
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

def getBaseUnit(name):
    return copy.deepcopy(knownBaseUnits[name])


#-------------------------------------------------------------

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
    