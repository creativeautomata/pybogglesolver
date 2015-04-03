"""
Module to generate solutions for Boggle grids.

Andrew Gillis  22 Dec. 2009

"""
import trie


class BoggleSolver(object):
    """
    This class uses an external words file as a dictionary of acceptable boggle
    words.  When an instance of this class is created, it sets up an internal
    dictionary to look up valid boggle answers.  The class' solve method can be
    used repeatedly to generate solutions for different boggle grids.

    """

    def __init__(self, xlen=None, ylen=None, max_letters=None, min_letters=3):
        """
        Create and initialize BoggleSolver instance.

        This creates the internal trie for fast word lookup letter-by-letter.
        Words that begin with capital letters and words that are not within the
        specified length limits are filtered out.

        Arguments:
        xlen        -- X dimension (width) of board.
        ylen        -- Y dimension (height) of board.
        max_letters -- Valid words must not have more than this many letters.
        min_letters -- Valid words must have at least this many letters.

        """
        if xlen is None:
            xlen = 4
        if ylen is None:
            ylen = 4
        assert(xlen > 1)
        assert(ylen > 1)
        board_size = xlen * ylen
        if max_letters is None:
            max_letters = board_size
        assert(min_letters > 1)
        assert(max_letters <= board_size)
        assert(min_letters <= max_letters)
        self.xlen = xlen
        self.ylen = ylen
        self.board_size = board_size
        self.min_letters = min_letters
        self.max_letters = max_letters
        self.adjacency = BoggleSolver._create_adjacency_matrix(xlen, ylen)
        self.trie = None


    def load_dictionary(self, words_file):
        """
        Load the file containing the reference words.

        Arguments:
        word_file   -- File containing valid words.  Each word must be on a
                       separate line in this file.

        Return:
        True if success, False if error.

        """
        try:
            word_count = self._create_dict_trie(words_file)
        except IOError:
            print 'ERROR: unable to open dictionary file:', words_file
            return False

        print 'loaded', word_count, 'words from dictionary'
        return True


    def solve(self, grid):
        """
        Generate all solutions for the given boggle grid.

        Arguments:
        grid -- A string of 16 characters representing the letters in a boggle
                grid, from top left to bottom right.

        Returns:
        A list of words found in the boggle grid.
        None if given invalid grid.

        """
        if self.trie is None:
            print 'ERROR: dictionary file not loaded'
            return None

        if len(grid) != self.board_size:
            print 'ERROR: invalid board'
            return None

        board = list(grid)
        trie = self.trie
        words = set()
        q = []
        adjs = self.adjacency

        for init_sq in xrange(len(adjs)):
            c = board[init_sq]
            q.append((init_sq, c, trie.get_child(c), [init_sq]))
            while q:
                parent_sq, prefix, pnode, seen = q.pop(0)
                pnode_get_child = pnode.get_child
                for cur_sq in adjs[parent_sq]:
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
        """
        Utility method to print a 4x4 boggle grid.

        Arguments:
        grid -- A string of X*Y characters representing the letters in a boggle
                grid, from top left to bottom right.

        """
        for y in xrange(self.ylen):
            print '+' + '---+' * self.xlen
            yi = y * self.xlen
            line = ['| ']
            for x in xrange(self.xlen):
                cell = grid[yi+x].upper()
                if cell == 'Q':
                    line.append('Qu')
                    line.append('| ')
                else:
                    line.append(cell)
                    line.append(' | ')
            print ''.join(line)
        print '+' + '---+' * self.xlen


    def find_substrings(self, string):
        """
        Find all valid substrings in the given string.

        This method is not necessary for the boggle solver, but is a utility
        for testing that all substrings of a word are correctly found.

        Arguments:
        string -- The string in which to search for valid substrings.

        Returns:
        List of substrings that are valid words.

        """
        found = set()
        for start in xrange(len(string)):
            cur = self.trie
            letters = [None] * self.max_letters
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


    def _create_dict_trie(self, words_file):
        """
        Private method to create the trie for finding words.

        Arguments:
        words_file  -- Path of file containing words for reference.

        Return:
        Count of words inserted into trie.

        """
        print 'creating dictionary...'
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
                word = word[:-1]
                # Skip words that are too long or too short.
                word_len = len(word)
                if word_len > self.max_letters or word_len < self.min_letters:
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

                #print 'adding word:', word
                root.insert(word)
                word_count += 1
        finally:
            f.close()

        print 'finished creating dictionary'
        self.trie = root
        return word_count


    @staticmethod
    def _create_adjacency_matrix(xlim, ylim):
        adj_list = [[]] * (ylim*xlim)

        for y in xrange(ylim):
            for x in xrange(xlim):
                # Current cell index = y * xlim + x
                adj = []
                adj_list[y*xlim + x] = adj

                # Look at row above current cell.
                cell_y = y-1
                if cell_y >= 0:
                    # Look to upper left.
                    cell_x = x-1
                    if cell_x >=0:
                        adj.append(cell_y*xlim + cell_x)
                    # Look above.
                    cell_x = x
                    adj.append(cell_y*xlim + cell_x)
                    # Look upper right.
                    cell_x = x+1
                    if cell_x < xlim:
                        adj.append(cell_y*xlim + cell_x)

                # Look at same row that current cell is on.
                cell_y = y
                # Look to left of current cell.
                cell_x = x-1
                if cell_x >=0:
                    adj.append(cell_y*xlim + cell_x)
                # Look to right of current cell.
                cell_x = x+1
                if cell_x < xlim:
                    adj.append(cell_y*xlim + cell_x)

                # Look at row below current cell.
                cell_y = y+1
                if cell_y < ylim:
                    # Look to lower left.
                    cell_x = x-1
                    if cell_x >=0:
                        adj.append(cell_y*xlim + cell_x)
                    # Look below.
                    cell_x = x
                    adj.append(cell_y*xlim + cell_x)
                    # Look to lower rigth.
                    cell_x = x+1
                    if cell_x < xlim:
                        adj.append(cell_y*xlim + cell_x)

        return adj_list

