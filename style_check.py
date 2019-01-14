import collections
import re
import sys

MatlabFile = collections.namedtuple(
    'MatlabFile', [
        'contents',  # contents of .m-file (one string)
        'lines',        # array of lines
        'comment_free'  # array of lines (blanks lines and comments stripped)
    ], defaults = [None, None, None])

### Rule 1: Scripts
# Scripts are allowed if the first invocations are
# 'clear' and 'close all'
#
# We will allow some comments and blank lines at the start.
#
# A file containing a function definition is also OK.
def rule_one(f):
    # match 'clear' and 'close all' (in either order)
    valid = True
    found_clear = False
    found_close_all = False
    found_crud = False
    for l in f.comment_free:
        if re.search(r'clear', l):
            found_clear = True
        if re.search(r'close\s+all', l):
            found_close_all = True
        if ((not found_clear) and (not found_close_all)):
            found_crud = True

    needfuls_present = found_close_all and found_clear
    if (not needfuls_present):
        print("Your file did not contain 'close all' and 'clear'!")
        valid = False
    if (needfuls_present and found_crud):
        print("Your file had invocations before 'close all' and 'clear'!")
        valid = False

    return valid

def parse_args():
    return sys.argv[1]

def strip_comments(ll):
    new_lines = []
    for l in ll:
        l = re.sub(r'\s*%.*', '', l)
        if l:
            new_lines.append(l)
    return new_lines

def read_file(filename):
    f = open(filename)
    c = f.read()
    l = c.splitlines(False)
    m = MatlabFile(contents = c, lines = l, comment_free = strip_comments(l))
    return m

def main():
    filename = parse_args()
    matlab_file = read_file(filename)
    valid = True
    valid &= rule_one(matlab_file)
    if (not valid):
        print("File not valid.")
        sys.exit(-1)
    else:
        print("File valid.")
        sys.exit(0)

main()
