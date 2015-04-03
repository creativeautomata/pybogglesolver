# Find words in X by Y boggle grids and display results interactively.
#
# This script uses the bogglesolver module to generate solutions to the boggle
# grids entered by a user.  The bogglesolver's internal dictionary is created
# once when the object is initialized.  It is then reused for subsequent
# solution searches.
#
# The user is prompted to input a string of x*y characters, representing the
# letters in a X by Y Boggle grid.  Use the letter 'q' to represent "qu".
#
# For example: "qadfetriihkriflv" represents the 4x4 grid:
# +---+---+---+---+
# | Qu| A | D | F |
# +---+---+---+---+
# | E | T | R | I |
# +---+---+---+---+
# | I | H | K | R |
# +---+---+---+---+
# | I | F | L | V |
# +---+---+---+---+
#
# This grid has 62 unique solutions using the default dictionary.
#
# Display help to see usage infomation: python boggle.py -h
#

__author__ = "Andrew Gillis"
__copyright__ = "Copyright 2009, Andrew Gillis"

import bogglesolver
import time
import sys
import os

ALPHA=0
LONGEST=1
SHORTEST=2
DEFAULT_DICT='boggle_dict.txt.gz'


def run_board(dict_file, xlen, ylen, sort_type, quiet_level, benchmark):
    if dict_file is None:
        dict_file = DEFAULT_DICT

    solver = bogglesolver.BoggleSolver(xlen, ylen)
    if not solver.load_dictionary(dict_file):
        return 1

    board_size = int(xlen * ylen)
    while(True):
        if benchmark:
            grid = []
            ord_a = ord('a')
            c = 0
            while len(grid) < board_size:
                if c == 26:
                    c = 0
                grid.append(chr(ord_a + c))
                c += 1
            grid = ''.join(grid)
        else:
            try:
                grid = raw_input('\nEnter %d letters from boggle grid: '
                                 % board_size)
            except KeyboardInterrupt:
                print
                break

        if not grid:
            break

        start_time = time.time()
        words = solver.solve(grid)
        elapsed = time.time() - start_time

        # If grid is invalid, ask for input again.
        if words is None:
            continue

        print '\nFound %d solutions for %dx%d grid in %0.2f msec:'\
              % (len(words), xlen, ylen, elapsed * 1000)

        if quiet_level < 2:
            if quiet_level < 1:
                solver.show_grid(grid)
            show_words(words, sort_type)

        if benchmark:
            time.sleep(1)
            continue

    return 0


def show_words(words, sort_type):
    words = list(words)

    if sort_type == ALPHA:
        # Sort words alphabetically
        words.sort()
        words.reverse()
    elif sort_type == LONGEST:
        # Sort by word length, longest to shortest.
        words.sort(cmp=lambda i,j: cmp(len(j), len(i)))
    elif sort_type == SHORTEST:
        # Sort by word length, shortest to longest,
        words.sort(cmp=lambda i,j: cmp(len(i), len(j)))

    # Display words in 4 columns (assumes 80-char wide display).
    while(words):
        w1 = words.pop().ljust(18)
        w2 = w3 = w4 = ''
        if words:
            w2 = words.pop().ljust(18)
        if words:
            w3 = words.pop().ljust(18)
        if words:
            w4 = words.pop().ljust(18)
        print w1, w2, w3, w4


if __name__ == '__main__':
    dict_file = None
    xlen = 4
    ylen = 4
    sort_type = ALPHA
    quiet_level = 0
    benchmark = False

    argv = list(sys.argv)
    prg = argv.pop(0)
    argc = len(argv)
    usage_msg = 'usage: python '+prg+ \
                ' [option].. [-x width] [-y height] [dictionary_file]'

    help_opt = False
    err_msg = None

    while argv:
        arg = argv.pop(0)
        argc -= 1
        if arg.startswith('-'):
            if arg == '-h' or arg == '--help':
                help_opt = True
            elif arg == '-l' or arg == '--longest':
                sort_type = LONGEST
            elif arg == '-s' or arg == '--shortest':
                sort_type = SHORTEST
            elif arg == '-x':
                if not argc:
                    err_msg = 'Missing X length (width) of board'
                    break
                xlen = int(argv.pop(0))
                argc -= 1
            elif arg == '-y':
                if not argc:
                    err_msg = 'Missing Y length (height) of board'
                    break
                ylen = int(argv.pop(0))
                argc -= 1
            elif arg == '-qq':
                quiet_level = 2
            elif arg == '-q':
                quiet_level = 1
            elif arg == '-b':
                benchmark = True
            else:
                err_msg = 'Unknown option: '+arg
                break
        else:
            if not os.path.isfile(arg):
                err_msg = 'Invalid dictionary file: '+arg
                break
            dict_file = arg

    if err_msg:
        print err_msg
        print usage_msg
        print 'Try '+prg+' -h for more information.'
        sys.exit(1)

    if help_opt:
        print usage_msg
        print '-b     : run benchmark test'
        print '-h     : print this help message and exit (also --help)'
        print '-l     : sort words longest-first'
        print '-q     : do not display grid'
        print '-qq    : do not display grid or solutions'
        print '-s     : sort words shortest-first'
        print '-x len : Width (X-length) of board.'
        print '-y len : Height (Y-length) of board.'
        print '\nDefault values:'
        print 'If -l or -s not specified, then words are sorted alphabetically.'
        print 'If -x is not specified, then x-length is set to 4.'
        print 'If -y is not specified, then y-length is set to 4.'
        print 'If no dictionary file is given, then use', DEFAULT_DICT
        sys.exit(0)

    rc = run_board(dict_file, xlen, ylen, sort_type, quiet_level, benchmark)
    sys.exit(rc)
