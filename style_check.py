import collections
import re
import sys

MatlabFile = collections.namedtuple(
    'MatlabFile', [
        'contents',  # contents of .m-file (one string)
        'lines'        # array of lines
    ])

### Rule 1: Scripts
# Scripts are allowed if the first invocations are
# 'clear' and 'close all'
#
# We will allow some comments and blank lines at the start.
#
# A file containing a function definition is also OK.

def parse_args():
    return sys.argv[1]

def read_file(filename):
    f = open(filename)
    c = f.read()
    l = c.splitlines(False)
    m = MatlabFile(contents = c, lines = l)
    return m

def main():
    filename = parse_args()
    matlab_file = read_file(filename)
    print(matlab_file.contents)
    print()
    print(matlab_file.lines)
    print()

main()
