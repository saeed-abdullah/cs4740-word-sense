

class WordMap:
    """
    Class for handling the collocations of words, by storing 
    and giving unique indexes to words added to it. 
    """

    def __init__(self):
        self.word_map = {}
        self.last_index = 0

    def add(self, word):
        """
        Adds a word to the map and returns its unique index

        param word: String word to be added to the index
        """
        word = self.prepare(word)

        if not self.in_map(word):
            self.last_index += 1
            self.word_map[word] = self.last_index
            return self.last_index
        else:
            self.word_map[word]

    def get(self, word):
        """
        Returns the unique index of the supplied word

        param word: string word to look for in the index
        """
        word = self.prepare(word)
        return self.word_map[word] if word in self.word_map else self.add(word)

    def pop(self, word):
        """
        Returns and removes the unique index of the supplied word 
        and returns -1 if the word is not in the map
        """
        word = self.prepare(word)
        return self.word_map.pop(word) if word in self.word_map else -1

    def in_map(self, word):
        """
        Checks if the word is already in the map index
        """
        return word in self.word_map

    def prepare(self, word):
        """
        Prepares the word for entry into the map index. Removes
        trailing and leading whitespace and lowercases the string
        """
        return word.lower().strip()

    def echo(self):
        print self.word_map