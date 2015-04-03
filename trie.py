ORD_A = ord('a')

class Trie(object):

    slots = ('_children', '_is_word')
    def __init__(self):
        self._children = [None] * 26
        self._is_word = False


    def insert(self, word):
        cur = self
        for l in word:
            next = cur.get_child(l)
            if next is None:
                #print 'new letter:', l
                new_node = Trie()
                cur._children[ord(l) - ORD_A] = new_node
                cur = new_node
            else:
                #print 'found letter:', l
                cur = next
        cur._is_word = True


    def contains(self, letter):
        return self._children[ord(letter) - ORD_A] is not None


    def is_word(self):
        return self._is_word


    def get_child(self, letter):
        return self._children[ord(letter) - ORD_A]


    def has_children(self):
        return any(self._children)


