# module convertTest.py
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

import unittest
from convert import *
from pyparsing import ParseException

class Test(unittest.TestCase):


    def testParserException(self):
        parseInput("10 km to mi")
        parseInput("10 m2 to mi2")
        parseInput("10 Ml to dm3")
        
        parseInput("10 m/s to km/h")
        parseInput("10 m/s2 to km/h2")
        parseInput("10 N to kg*m/s2")
        parseInput("10 Ml to dm3")
        
        self.assertRaises(ParseException, lambda: parseInput("10 litres to m3"))
        self.assertRaises(ParseException, lambda: parseInput("10 Hl to m3"))
        self.assertRaises(ParseException, lambda: parseInput("10 km3 to Km3"))

        
    
    def testUnitFromExpr(self):
        res = parseInput("10 N to kg*m/s2")
        
        srcUnit = unitFromExpr(res.srcExpr)
        dstUnit = unitFromExpr(res.dstExpr)
        
        self.assertEqual(srcUnit.scale, 0.001)
        self.assertEqual(srcUnit.dimensions, {'M':1, 'L':1, 'T':-2})
        self.assertEqual(dstUnit.scale, 1000)
        self.assertEqual(dstUnit.dimensions, {'M':1, 'L':1, 'T':-2})
        
   
    def testUnitFromExpr2(self):     
        res = parseInput("1 m to m2")
        
        srcUnit = unitFromExpr(res.srcExpr)
        dstUnit = unitFromExpr(res.dstExpr)
        
        self.assertEqual(srcUnit.scale, 1)
        self.assertEqual(srcUnit.dimensions, {'L':1})
        self.assertEqual(dstUnit.scale, 1)
        self.assertEqual(dstUnit.dimensions, {'L':2})
        
        
    def testUnitFromExpr3(self):     
        res = parseInput("1 ft to mi2")
        
        srcUnit = unitFromExpr(res.srcExpr)
        dstUnit = unitFromExpr(res.dstExpr)
        
        self.assertEqual(srcUnit.scale, 0.3048)
        self.assertEqual(srcUnit.dimensions, {'L':1})
        self.assertEqual(dstUnit.scale, 1609.344 ** 2)
        self.assertEqual(dstUnit.dimensions, {'L':2})
        

    def testUnitOfMeasurement(self):
        unit1 = UnitOfMeasurement(12, {'L':3, 'T':-2})
        unit2 = UnitOfMeasurement(2, {'M':2, 'L':-1})
        self.assertNotEqual(unit1, unit2)
        
        unit3 = unit1 * unit2
        self.assertEqual(unit3, UnitOfMeasurement(24, {'L':2, 'T':-2, 'M':2}) )
    
        unit3 = unit1 / unit2
        self.assertEqual(unit3, UnitOfMeasurement(6, {'L':4, 'T':-2, 'M':-2}) )

        self.assertEqual(UnitOfMeasurement(12, {'L':1}).dimensionsString(), 'length')
        self.assertEqual(UnitOfMeasurement(12, {'L':1, 'T':-2}).dimensionsString(), 'acceleration')

        self.assertFalse(unit1.isCompatible(unit2))
        self.assertFalse(unit2.isCompatible(unit1))
        
        unit2 = UnitOfMeasurement(2, {'L':3, 'T':-2})
        self.assertTrue(unit1.isCompatible(unit2))
        self.assertTrue(unit2.isCompatible(unit1))
        
        self.assertEqual(unit1.conversionFactor(unit2), 6)
        self.assertEqual(unit2.conversionFactor(unit1), 2/12)

    
    def testConvert(self):
        self.assertRaises(RuntimeError, lambda: convertString("1 m to m2"))
        
    def testConvert2(self):
        self.assertEqual(convertString("1 m to cm"), 100)
        self.assertEqual(convertString("1 m to mm"), 1000)
        self.assertEqual(convertString("1 ft/s to km/h"), 1.09728)
        self.assertAlmostEqual(convertString("1 ft/s2 to km/s2"), 0.0003048, delta=0.00000001)
        self.assertEqual(convertString("1 m2 to cm2"), 10000)
        self.assertAlmostEqual(convertString("1 m3 to mm3"), 1000000000, delta=0.001)
        self.assertEqual(convertString("10 1/s to Hz"), 10)
        self.assertAlmostEqual(convertString("3.6 usd/gal to eur/l"), 0.696105540546, delta=0.00000001)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testParseInput']
    unittest.main()
    