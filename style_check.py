import collections
import re
import sys


MatlabFile = collections.namedtuple(
    'MatlabFile', [
        'contents',  # contents of .m-file (one string)
        'lines',        # array of lines
        'comment_free'  # array of lines (blanks lines and comments stripped)
    ], defaults = [None, None, None])


# Make an RE which matches the word x
def word_re(x):
    return r'(?<!\w)' + x + r'(?!\w)'


### Rule 1: Scripts
# Scripts are allowed if the first invocations are
# 'clear' and 'close all' (and optionally 'clc')
#
# We will allow some comments and blank lines at the start.
#
# A file containing a function definition is also OK.
def rule_one(f):
    # match either 'clear' and 'close all' (in either order)
    # or 'function'
    valid = True
    found_clear = False
    found_close_all = False
    found_clc = False
    found_function = False
    found_crud = False
    for i, l in enumerate(f.comment_free):
        if not l:
            continue
        if re.search(word_re('clear'), l):
            found_clear = True
        if re.search(word_re(r'close\s+all'), l):
            found_close_all = True
        if re.search(word_re(r'function'), l):
            found_function = True
        if re.search(word_re(r'clc'), l):
            found_clc = True
        if (((not found_clear) and (not found_close_all)) and
            (not found_function) and (not found_clc)):
            found_crud = True

    valid_script = (found_close_all and found_clear)
    if (not valid_script) and (not found_function):
        print("Your script file did not contain 'close all' and 'clear'!")
        valid = False
    if (valid_script and found_crud):
        print("Your script file had invocations before 'close all' and 'clear'!")
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
    for i, l in enumerate(f.comment_free):
        if re.search(word_re('function'), l):
            if in_function:
                print("Nested function detected!")
                print("Line %d: %s" % (i+1, l))
                return False
            else:
                in_function = True
        #   while (b==0); if (a[1] == 1); b = 2; end;
        #   end
        control_words = ['for', 'while', 'switch', 'try', 'if', 'parfor']
        word_res = [word_re(x) for x in control_words]
        nonmatch_group = r'(?:' + '|'.join(word_res) + ')'
        lookahead = r'(?=' + '|'.join(word_res + ['$']) + ')'
        # m = re.findall(r'(?:for|while|switch|try|if|parfor).+?(?=for|while|switch|try|if|parfor|$)', l)
        m = re.findall(nonmatch_group + '.+?' + lookahead, l)
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
def rule_three(f):
    for i, l in enumerate(f.comment_free):
        m = re.search(r'(' + word_re('figure') + ')\s*(\()?', l)
        if m and m.groups()[1] is None:
            print("'Figure' invoked with no handle!")
            print("Line %d: %s" % (i+1, l))
            return False
    return True


# rule 4: no overloading builtins
def rule_four(f):
    words = ['zeros', 'ones', 'rand', 'true', 'false', 'eye', 'diag', 'blkdiag', 'cat', 'horzcat', 'vertcat', 'repelem', 'repmat',
             'linspace', 'logspace', 'freqspace', 'meshgrid', 'ndgrid',
             'length', 'size', 'ndims', 'numel', 'isscalar', 'issorted', 'issortedrows', 'isvector', 'ismatrix', 'isrow', 'iscolumn', 'isempty']
    word_res = [word_re(x) for x in words]
    words_re = '|'.join(word_res)
    # print(words_re)
    for i, l in enumerate(f.comment_free):
        m = re.search(r'(' + words_re + r')\s*=', l)
        if m:
            w = m.groups(1)
            print("Builtin %s overloaded!" % (w))
            print("Line %d: %s" % (i+1, l))
            return False
    return True


# rule 5: max line len 80 chars
def rule_five(f):
    for i, l in enumerate(f.lines):
        if (len(l) > 80):
            print("Overlong line (80-char limit)!")
            print("Line %d: %s" % (i+1, l))
            return False
    return True


# rule 6: one statement per line
def rule_six(f):
    for i, l in enumerate(f.comment_free):
        in_square_bracket = 0
        hit_semicolon = False
        for c in l:
            if c == '[':
                in_square_bracket += 1
                continue
            if c == ']':
                in_square_bracket -= 1
                continue
            if c == ';' and in_square_bracket == 0:
                hit_semicolon = True
                continue
            if c != ' ' and hit_semicolon:
                print("Multiple statements on line!")
                print("Line %d: %s" % (i+1, l))
                return False
    return True

def strip_strings(l):
    stripped = ""
    last_char = None
    in_string = False
    for c in l:
        if c != '\'' and in_string:
            continue
        if c == '\'' and in_string:
            in_string = False
            stripped += c
            continue
        if c == '\'' and (not in_string):
            if (re.match(r'[a-z0-9A-Z]', last_char)):
                # Transpose operator
                stripped += c
                continue
            else:
                stripped += c
                in_string = True
                continue
        stripped += c
        last_char = c
    return stripped

# rule 7: 2-space indent
def rule_seven(f):
    scope_increasers = ['while', 'for', 'if', 'function', 'parfor', 'else']
    scope_decreasers = ['end', 'else']
    scope_increase_res = [word_re(x) for x in scope_increasers]
    scope_increase_re =  '|'.join(scope_increase_res)
    scope_decrease_res = [word_re(x) for x in scope_decreasers]
    scope_decrease_re =  '|'.join(scope_decrease_res)

    expected_indent = 0
    INDENT = 2
    valid = True
    run_on_line = False
    for i, l in enumerate(f.comment_free):
        l_no_string = strip_strings(l)
        # Skip blank lines
        if re.match('^\s*$', l_no_string):
            continue

        if re.search(scope_decrease_re, l_no_string):
            expected_indent -= INDENT

        # Check indent
        indent_re = r'^' + r' ' * expected_indent
        if not run_on_line:
            indent_re +=  r'[^\s]'
        if not (re.search(indent_re, l_no_string)):
            actual_indent = len(l_no_string) - len(l_no_string.lstrip(' '))
            print("Indent problem! Expected %d, found %d." % (expected_indent, actual_indent))
            print("Line %d: %s" % (i+1, l))
            valid = False

        if re.search(scope_increase_re, l_no_string):
            expected_indent += INDENT

        if re.search('...$', l_no_string):
            run_on_line = True
        else:
            run_on_line = False


    return valid


# rule 8: one space char around operators (not ':();')
def rule_eight(f):
    passed = True
    # define list of operators
    ops = ['+', '-', '.*', '*', './', '/', '.\\', '\\', '.^', '^',
           '==', '=', '~=', '<', '<=', '>', '>=', '&', '|', '&&', '||', '~']
    # omitting transpose operators, as you couldn't write <A '>
    # skip strings

    # scan to establish what characters can legitimately precede / follow each operator,
    # other than space (must be from another operator)
    ops_data = []
    for o in ops:
        pres = " "
        posts = " "
        if o == "+" or o == "-":
            # Allow for unary operators
            pres += re.escape('(')
            posts += '\d\.\w'
        for o2 in ops:
            if (o == o2):
                continue
            if len(o2) > 1 and o2[1] == o:
                pres += re.escape(o2[0])
            if o2[0] == o and len(o2) > 1:
                posts += re.escape(o2[1])
        ops_data += [(re.escape(o), pres, posts)]
    # print(ops_data)

    # scan the list of operators to define
    space_pre = lambda x: r'(  |[^' + x[1] + '])' + x[0]
    space_post = lambda x: x[0] + r'(  |[^' + x[2] + '])'
    op_res = [f(x) for x in ops_data for f in (space_pre, space_post)]
    # Match against operator preceded by non-space
    # or operator followed by non-space.
    op_re = '|'.join(op_res)
    # print(op_re)
    for i, l in enumerate(f.comment_free):
        l_no_string = strip_strings(l)

        m = re.search(op_re, l_no_string)
        if m:
            print("One space around operators!")
            print("Line %d: %s" % (i+1, l))
            passed = False
        m = re.search(r' ,|(,([^ ]|  ))', l_no_string)
        if m:
            print("No space before ',', one space after!")
            print("Line %d: %s" % (i+1, l))
            passed = False

    return passed



# rule 9: underscores in var names
# rule 10: two blank lines between function defs
# rule 11: comments


def parse_args():
    return sys.argv[1]

def strip_comments(ll):
    new_lines = []
    for i, l in enumerate(ll):
        l = re.sub(r'\s*%.*', '', l)
        new_lines.append(l)  # Preserving blank lines to preserve line nums.
    return new_lines

def read_file(filename):
    f = open(filename)
    c = f.read()
    l = c.splitlines(False)  # False: discard line end chars
    m = MatlabFile(contents = c, lines = l, comment_free = strip_comments(l))
    return m

def main():
    filename = parse_args()
    matlab_file = read_file(filename)
    valid = True
    valid &= rule_one(matlab_file)
    valid &= rule_two(matlab_file)
    valid &= rule_three(matlab_file)
    valid &= rule_four(matlab_file)
    valid &= rule_five(matlab_file)
    valid &= rule_six(matlab_file)
    valid &= rule_seven(matlab_file)
    valid &= rule_eight(matlab_file)

    if (not valid):
        print("File not valid.")
        sys.exit(-1)
    else:
        print("File probably OK.")
        sys.exit(0)

main()
