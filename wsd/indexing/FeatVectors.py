import nltk
import re
import WordMap

class FeatVectors:

    FILE = ""
    word_map = None

    def __init__(self, inputfile = ""):
        self.word_map = WordMap.WordMap()

        if not inputfile == "":
            self.FILE = inputfile

    def open_file(self, file_name = "../Data/practice.data.txt"):
        self.FILE = open(file_name)

    def get_file(self):
        return self.FILE

    def map_file(self, inputfile):
        """
        Takes a file object and maps out each individual line in
        the file to the map format. 

        returns an array of dictionarys containing each line object
        """
        file_map = []

        for line in inputfile:
            file_map.append(self.map_line(line))

        return file_map

    def map_line(self, line):
        """
        Takes an individual line and parse out the components of the line 
        given the format "word.pos t0 t1 ... tk @ context @ target @ context"
        
        returns a dictionary containing those individual elements
        """
        line_map = {}

        line_map['word']     = line[0 : line.find('.')]
        line_map['pos']      = line[line.find('.') + 1 : line.find(' ')]
        line_map['sense']    = line[line.find(" ") + 1 : line.find("@")]
        line_map['context']  = context = line[line.find("@") + 1:]
        line_map['coll']     = coll = self.find_coll(context)
        line_map['coll_map'] = self.map_coll(coll)

        return line_map

    def find_coll(self, context, dist = 2):
        """
        Finds the collocated words surrounding the @target@ word 
        in the context

        returns a string of space separated collocations.
        """
        word_list = context.split(' ')
        pattern = re.compile('(@?[a-zA-Z]+@)')

        i = 0
        for word in word_list:
            if pattern.match(word):
                word_list.pop(i)
                break
            i += 1

        # Need to fix the possibility of reverting to the 
        # end of the list if the word appears at the
        # beginning

        return " ".join(word_list[i-dist : i+dist])

    def map_coll(self, coll):
        words = coll.split()
        nums = []

        for word in words:
            nums.append(str(self.word_map.get(word)))

        return " ".join(nums)

    def find_word_lines(self, inputfile, word):
        """
        Finds all the lines in a given file object that start with 
        the supplied word returns a list containing those lines

        returns a list of strings containing the word sense information
        """
        lines = []

        for line in inputfile:
            if line.startswith(word):
                lines.append(line)

        return lines

    def dis_word(self, word):
        
        wFile = self.find_word_lines(self.get_file(), word)
        wMap = self.map_file(wFile)

        return wMap
