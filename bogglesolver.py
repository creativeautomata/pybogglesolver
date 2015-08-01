"""
Module to generate solutions for Boggle grids.

Andrew Gillis 22 Dec. 2009

"""
from __future__ import print_function
import os
import sys
import collections

import trie

if sys.version < '3':
    range = xrange

class BoggleSolver(object):
    """
    This class uses an external words file as a dictionary of acceptable boggle
    words.  When an instance of this class is created, it sets up an internal
    dictionary to look up valid boggle answers.  The class' solve method can be
    used repeatedly to generate solutions for different boggle grids.

    """

    def __init__(self, words_file, xlen=4, ylen=4, pre_compute_adj=False):
        """Create and initialize BoggleSolver instance.

        This creates the internal trie for fast word lookup letter-by-letter.
        Words that begin with capital letters and words that are not within the
        specified length limits are filtered out.

        Arguments:
        xlen        -- X dimension (width) of board.
        ylen        -- Y dimension (height) of board.
        pre_compute_adj -- Pre-compute adjacency matrix.

        """
        assert(xlen > 1)
        assert(ylen > 1)
        self.xlen = xlen
        self.ylen = ylen
        self.board_size = xlen * ylen
        if pre_compute_adj:
            self.adjacency = BoggleSolver._create_adjacency_matrix(xlen, ylen)
        else:
            self.adjacency = None
        self.trie = BoggleSolver._load_dictionary(
            words_file, self.board_size, 3)

    def solve(self, grid):
        """Generate all solutions for the given boggle grid.

        Arguments:
        grid -- A string of 16 characters representing the letters in a boggle
                grid, from top left to bottom right.

        Returns:
        A list of words found in the boggle grid.
        None if given invalid grid.

        """
        if self.trie is None:
            raise RuntimeError('words file not loaded')

        if len(grid) != self.board_size:
            raise RuntimeError('invalid board')

        board = list(grid)
        trie = self.trie
        words = set()
        q = collections.deque()
        adjs = self.adjacency

        for init_sq in range(self.board_size):
            c = board[init_sq]
            q.append((init_sq, c, trie.get_child(c), [init_sq]))
            while q:
                parent_sq, prefix, pnode, seen = q.popleft()
                pnode_get_child = pnode.get_child
                if adjs:
                    adj = adjs[parent_sq]
                else:
                    adj = self._calc_adjacency(self.xlen, self.ylen, parent_sq)
                for cur_sq in adj:
                    if cur_sq in seen:
                        continue
                    c = board[cur_sq]
                    cur_node = pnode_get_child(c)
                    if cur_node is None:
                        continue
                    s = prefix + c
                    q.append((cur_sq, s, cur_node, seen + [cur_sq]))
                    if cur_node._is_word:
                        if s[0] == 'q':
                            # Rehydrate q-words with 'u'.
                            words.add('qu' + s[1:])
                        else:
                            words.add(s)

        return words

    def show_grid(self, grid):
        """Utility method to print a 4x4 boggle grid.

        Arguments:
        grid -- A string of X*Y characters representing the letters in a boggle
                grid, from top left to bottom right.

        """
        for y in range(self.ylen):
            print('+' + '---+' * self.xlen)
            yi = y * self.xlen
            line = ['| ']
            for x in range(self.xlen):
                cell = grid[yi+x].upper()
                if cell == 'Q':
                    line.append('Qu')
                    line.append('| ')
                else:
                    line.append(cell)
                    line.append(' | ')
            print(''.join(line))
        print('+' + '---+' * self.xlen)

    def find_substrings(self, string):
        """Find all valid substrings in the given string.

        This method is not necessary for the boggle solver, but is a utility
        for testing that all substrings of a word are correctly found.

        Arguments:
        string -- The string in which to search for valid substrings.

        Returns:
        List of substrings that are valid words.

        """
        found = set()
        for start in range(len(string)):
            cur = self.trie
            letters = [None] * self.board_size
            count = 0

            for l in string[start:]:
                letters[count] = l
                count += 1
                cur = cur.get_child(l)
                if cur is None:
                    break
                if cur._is_word:
                    found.add(''.join(letters[:count]))
                if not cur.has_children():
                    break

        return found

    @staticmethod
    def _load_dictionary(words_file, max_len, min_len):
        """Private method to create the trie for finding words.

        Arguments:
        words_file  -- Path of file containing words for reference.

        Return:
        Count of words inserted into trie.

        """
        if not os.path.isfile(words_file):
            raise RuntimeError('words file not found: ' + words_file)

        print('creating dictionary...')
        root = trie.Trie()
        word_count = 0
        if words_file.endswith('gz'):
            import gzip
            f = gzip.open(words_file)
        elif words_file.endswith('bz2'):
            import bz2
            f = bz2.BZ2File(words_file)
        else:
            f = open(words_file)
        try:
            for word in f:
                if sys.version < '3':
                    word = word.strip()
                else:
                    word = word.strip().decode("utf-8")
                # Skip words that are too long or too short.
                word_len = len(word)
                if word_len > max_len or word_len < min_len:
                    continue
                # Skip words that start with capital letter.
                if word[0].isupper():
                    continue

                if word[0] == 'q':
                    # Skip words starting with q not followed by u.
                    if word[1] != 'u':
                        continue
                    # Remove "u" from q-words so that only the q is matched.
                    word = 'q' + word[2:]

                root.insert(word)
                word_count += 1
        finally:
            f.close()

        print('Loaded', word_count, 'words from file.')
        return root

    @staticmethod
    def _create_adjacency_matrix(xlim, ylim):
        adj_list = [[]] * (ylim * xlim)
        for i in range(ylim * xlim):
            # Current cell index = y * xlim + x
            adj = BoggleSolver._calc_adjacency(xlim, ylim, i)
            adj_list[i] = adj

        return adj_list

    @staticmethod
    def _calc_adjacency(xlim, ylim, sq):
        adj = []
        y = int(sq / xlim)
        x = sq - (y * xlim)

        # Look at row above current cell.
        if y-1 >= 0:
            above = sq - xlim
            # Look to upper left.
            if x-1 >= 0:
                adj.append(above - 1)
            # Look above.
            adj.append(above)
            # Look upper right.
            if x+1 < xlim:
                adj.append(above + 1)

        # Look at same row that current cell is on.
        # Look to left of current cell.
        if x-1 >= 0:
            adj.append(sq - 1)
        # Look to right of current cell.
        if x+1 < xlim:
            adj.append(sq + 1)

        # Look at row below current cell.
        if y+1 < ylim:
            below = sq + xlim
            # Look to lower left.
            if x-1 >= 0:
                adj.append(below - 1)
            # Look below.
            adj.append(below)
            # Look to lower rigth.
            if x+1 < xlim:
                adj.append(below + 1)

        return adj
