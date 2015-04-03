NAME:
    boggle.py - interactively find and display words in X by Y Boggle grids.

SYNOPSYS:
    | python boggle.py [option].. [-x width] [-y height] [dictionary_file]
    | -b     : benchmark test
    | -h     : print this help message and exit (also --help)
    | -l     : sort words longest-first
    | -q     : do not display grid
    | -qq    : do not display grid or solutions
    | -s     : sort words shortest-first
    | -x len : Width (X-length) of board.
    | -y len : Height (Y-length) of board.

    | Default values:
    | If -l or -s not specified, then words are sorted alphabetically.
    | If -x is not specified, then x-length is set to 4.
    | If -y is not specified, then y-length is set to 4.
    | If no dictionary file is given, then use boggle_dict.txt

DESCRIPTION:
    This script uses the bogglesolver module to generate solutions to the
    boggle grids entered by a user.  The bogglesolver's internal dictionary is
    created once when the object is initialized.  It is then reused for
    subsequent solution searches.

    The user is prompted to input a string of x*y characters, representing the
    letters in a X by Y Boggle grid.  Use the letter 'q' to represent "qu".

    For example: "qadfetriihkriflv" represents the 4x4 grid::

     +---+---+---+---+
     | Qu| A | D | F |
     +---+---+---+---+
     | E | T | R | I |
     +---+---+---+---+
     | I | H | K | R |
     +---+---+---+---+
     | I | F | L | V |
     +---+---+---+---+

    The default reference dictionary is included boggle_dict.txt, which is used
    if no dictionary is specified on the command line.  This dictionary
    includes plurals to words, which most dictionaries do not.

AUTHOR:
    Andrew Gillis - 08 Feb 2011
