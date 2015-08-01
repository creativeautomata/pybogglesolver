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
from __future__ import print_function
import time
import sys
import os

import bogglesolver

__author__ = "Andrew Gillis"
__copyright__ = "Copyright 2009, Andrew Gillis"

if sys.version < '3':
    input = raw_input
    range = xrange

ALPHA = 0
LONGEST = 1
SHORTEST = 2
DEFAULT_WORDS = 'boggle_dict.txt.gz'


def run_board(words_file, xlen, ylen, sort_type, quiet_level, benchmark,
              pre_compute_adj):
    if words_file is None:
        words_file = DEFAULT_WORDS

    solver = bogglesolver.BoggleSolver(words_file, xlen, ylen, pre_compute_adj)
    board_size = solver.board_size

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
                grid = input('\nEnter %d letters from boggle grid: '
                             % board_size)
            except KeyboardInterrupt:
                print()
                break

        if not grid:
            break

        start_time = time.time()
        words = solver.solve(grid)
        elapsed = time.time() - start_time

        # If grid is invalid, ask for input again.
        if words is None:
            continue

        print('\nFound %d solutions for %dx%d grid in %0.2f msec:'
              % (len(words), xlen, ylen, elapsed * 1000))

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
        if sys.version < '3':
            words.sort(cmp=lambda i, j: cmp(len(j), len(i)))
        else:
            words.sort(key=len)
    elif sort_type == SHORTEST:
        # Sort by word length, shortest to longest,
        if sys.version < '3':
            words.sort(cmp=lambda i, j: cmp(len(i), len(j)))
        else:
            words.sort(key=len, reverse=True)

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
        print(w1, w2, w3, w4)


def main():
    import argparse
    ap = argparse.ArgumentParser(
        description='Find words in X by Y boggle grids',
        epilog='home page: https://github.com/gammazero/pybogglesolver')

    ap.set_defaults(quiet_level=0)

    ap.add_argument('-x', type=int, dest='xlen', default=4,
                    help='Width (X-length) of board.')
    ap.add_argument('-y', type=int, dest='ylen', default=4,
                    help='Height (Y-length) of board.')
    ap.add_argument('-b', action='store_true', dest='benchmark',
                    help='Run benchmark test.')
    ap.add_argument('-p', action='store_true', dest='pre_compute_adj',
                    help='Pre-compute adjacency matrix.')
    ap.add_argument('--longest', '-l', action='store_const', const=LONGEST,
                    dest='sort_type', help='Sort words longest-first.')
    ap.add_argument('--shortest', '-s', action='store_const', const=SHORTEST,
                    dest='sort_type', help='Sort words shortest-first.')
    ap.add_argument('-q', action='store_const', const=1,
                    dest='quiet_level',  help='Do not display grid.')
    ap.add_argument('-qq', action='store_const', const=2, dest='quiet_level',
                    help='Do not display grid or solutions.')
    ap.add_argument('words_file', nargs='?', default=DEFAULT_WORDS,
                    help='File containing valid words, separated by newline.')
    args = ap.parse_args()

    if not os.path.isfile(args.words_file):
        print('Invalid words file: ', args.words_file, file=sys.stderr)
        return 1

    try:
        rc = run_board(args.words_file, args.xlen, args.ylen, args.sort_type,
                       args.quiet_level, args.benchmark, args.pre_compute_adj)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1

    return rc


if __name__ == '__main__':
    sys.exit(main())
