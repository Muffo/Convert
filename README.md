# Convert

Textual python unit converter

## Usage and examples

Run the software from the command line:

        python convert.py <value> <srcUnit> to <dstUnit>

The unit of measurements can be a complex expression containing multiplications, divisions and exponents.

Basic conversion:

    $ python convert.py 1 mi to m
    1609.344


Conversion with expressions:

    $ python convert.py 10 km/l to mi/gal
    23.5214583085

    $ python convert.py 10 km/h to m/s
    2.77777777778

    $ python convert.py 1 km2 to m2
    1000000.0


The conversion between two UnitOfMeasurement can be done only if those are compatible.
In other words, it's not possible to convert meter (length) to seconds (time):

    $ python convert.py 1 m to s
    Incompatible type length and time



## Installation

Convert is a single file that can be used directly from the command line.

It requires the library pyparsing:

    easy_install pyparsing

