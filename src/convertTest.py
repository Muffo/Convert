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
from convert import parseInput
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

    def testParseInput(self):
        res = parseInput("10 km to mi")
        print res
        self.assertEqual(res.value, '10')
        self.assertEqual(res.srcUnit.prefix, 'k')
        self.assertEqual(res.srcUnit.basicUnit, 'm')
        self.assertEqual(res.dstUnit.basicUnit, 'mi')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testParseInput']
    unittest.main()
    