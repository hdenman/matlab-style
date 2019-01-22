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

# rule 2: nested functions not allowed
#
# See https://uk.mathworks.com/help/matlab/ref/end.html
#
# 'end' terminates 'for', 'while', 'switch', 'try', 'if', and 'parfor'
# statements. Without an end statement, for, while, switch, try, if, and parfor
# wait for further input. Each end is paired with the closest previous unpaired
# for, while, switch, try, if, or parfor and serves to delimit its scope.
#
# 'end' also marks the termination of a function. Although it is sometimes
# optional, use end for better code readability. If your function contains one
# or more nested functions, then you must terminate every function in the file,
# whether nested or not, with end. This includes primary, nested, private, and
# local functions.
#
# If your script contains local functions, then you must terminate every local
# function in the file with end.
#
# The end function also serves as the last index in an indexing expression. In
# that context, end is the same as size(X,k) when used as part of the kth index
# into array X. Examples of this use are X(3:end) to select the third through
# final elements of the array, and X(1,1:2:end-1) to select all even elements of
# the first row, excluding the last element. When using end to grow an array, as
# in X(end+1)=5, make sure X exists first.

def rule_two(f):
    in_function = False
    compound_depth = 0
    for l in f.comment_free:
        if re.search(r'function', l):
            if in_function:
                print("Nested function detected!")
                return False
            else:
                in_function = True
        #   while (b==0); if (a[1] == 1); b = 2; end;
        #   end
        m = re.findall(r'(?:for|while|switch|try|if|parfor).+?(?=for|while|switch|try|if|parfor|$)', l)
        if m:
            compound_depth += len(m)
        if re.search(r'end(?!.*\))', l):  # 'end' not followed by ')'
            if compound_depth > 0:
                compound_depth -= 1
            elif in_function:
                in_function = False
            else:
                print("Warning warning!  Parse error for nested function check!")
    return True

# rule 3: figure handles required
# rule 4: no overloading builtins
# rule 5: max line len 80 chars
# rule 6: one statement per line
# rule 7: 2-space indent
# rule 8: one char around operators (not ':();')
# rule 9: underscores in var names
# rule 10: two blank lines between function defs
# rule 11: commenst


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
    valid &= rule_two(matlab_file)
    if (not valid):
        print("File not valid.")
        sys.exit(-1)
    else:
        print("File valid.")
        sys.exit(0)

main()
