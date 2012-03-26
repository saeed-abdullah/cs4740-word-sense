import WordMap
import pickle
import re

class FeatVectors:

    def __init__(self, inputfile):
        self.pklfile = inputfile

        try:
            self.word_map = pickle.load(open(inputfile))
        except:
            self.word_map = WordMap.WordMap()

    def open_file(self, file_name):
        self.FILE = open(file_name)

    def get_file(self):
        return self.FILE

    def write_map(self, pkl_file = None):
        """
        Writes the current wordmap to a pickle file for future use.
        Needs to have a pickle file available to it
        """
	if pkl_file == None:
	    pkl_file = self.pklfile

        pickle.dump(self.word_map, open(pkl_file, "w"))

    def map_file(self, file_lines):
        """
        Takes a file object and maps out each individual line in
        the file to the map format.

        returns an array of dictionarys containing each line object

        param
        -----
        file_lines: A file object or list of strings with lines of the format
            "word.pos t0 t1 ... tk @ context @ target @ context" to be mapped
        """
        file_map = []

        for line in file_lines:
            file_map.append(self.map_line(line))

        return file_map

    def map_line(self, line):
        """
        Takes an individual line and parse out the components of the line
        given the format "word.pos t0 t1 ... tk @ context @ target @ context"

        returns a dictionary containing those individual elements

        param
        -----
        line: An individual line containing WSD information
        """
        line_map = {}

        line_map['word']     = line[0 : line.find('.')]
        line_map['pos']      = line[line.find('.') + 1 : line.find(' ')]
        line_map['sense']    = line[line.find(" ") + 1 : line.find("@")]

        context = line[line.find("@") + 1:]
        line_map['context']  = context
        coll = self.find_coll(context)
        line_map['coll']     =  coll

        line_map['coll_map'] = self.map_coll(coll)

        return line_map

    def find_coll(self, context, dist = 2):
        """
        Finds the collocated words surrounding the @target@ word 
        in the context

        returns a string of space separated collocations.

        param
        -----
        context: The context string surrounding the target word
        dist: The number of words leading and trailing to base
            collocations off of
        """
        if self.coll_dist:
            dist = self.coll_dist

        word_list = context.strip().split(' ')
        left = right = dist
        pattern = re.compile('(@?[a-zA-Z]+@)')

        i = 0
        for word in word_list:
            if pattern.match(word):
                word_list.pop(i)
                break
            i += 1

        # Check to see if the collocation distance extends beyond the
        # size of the word list
        # Should we handle them like this or replacing empty spaces with 0s
        listlen = len(word_list)
        if i < left: 
            right = right + (left - i)
            left = i
        if i + right > listlen:
            diff = listlen - i
            l_change = left + (right-diff)
            left = l_change if not l_change > i else i
            right = diff

        coll_words = word_list[i-left:i+right]

        if len(coll_words) < dist*2:
            while len(coll_words) < dist*2:
                coll_words.append("0")
        
        return " ".join(coll_words)

    def map_coll(self, coll):
        """
        Takes the collocation string and maps the selected term to
        indexed numbers that are unique for each word type

        param 
        -----
        coll: The collocations string with words separated
            by spaces
        """
        words = coll.split()
        nums = []

        for word in words:
            nums.append(str(self.word_map.get(word)))

        return " ".join(nums)

    def find_word_lines(self, file_lines, word):
        """
        Finds all the lines in a given file object that start with 
        the supplied word returns a list containing those lines

        returns a list of strings containing the word sense information

        param 
        -----
        file_lines: A file or list of strings to fetch the congruent 
            word information from 

        word: The word and part of speach to search and build the list 
            on. Format as <word>.pos, e.g. begin.v
        """
        lines = []

        for line in file_lines:
            if line.startswith(word):
                lines.append(line)

        return lines

    def dis_word(self, word):
        """
        Looks for a specific word and extracts the lines that are associated
        with that word and performs the mapping for each line that is 
        found

        Returns an array of dictionaries containing the sense information
        for the given word

        param
        -----
        word: The word and part of speach to search and build the list 
            on. Format as <word>.pos, e.g. begin.v
        """
        wFile = self.find_word_lines(self.get_file(), word)
        wMap = self.map_file(wFile)

        return wMap

    def dis_file(self, word, fileinput, fileoutput, coll_dist = 2):
        """
        Creates the feature vectors for a file by mapping the words 
        indexes and outputs a file that can be read by datautil.py
        to create an arff file for Machine learning

        param
        -----
        word: The string word to build the feature vectors across the
            file
        fileinput: The location of the word sense data with each line
            in the format "word.pos t0 t1 ... tk @ context @ target @ context"
        fileoutput: the location of the file to output to the for 
            the input file for Learn.java
        coll_dist: The number of previous and post collocated words 
            to get when looking at the context of a word. 
        """
        import datautil

        self.coll_dist = coll_dist
        
        word_lines = self.find_word_lines(open(fileinput), word)
        fileoutput = open(fileoutput, 'w')

        fmap = self.map_file(word_lines)

        # Adding Hee's strip file code
        fmap = self.strip_file_map(fmap)
        
        if len(fmap) == 0:
            exit("No lines were found for that word")

        feature_count = coll_dist * 2
        class_count = len(fmap[0]['sense'].strip().split(" "))

        file_lines = self.format_headers( feature_count, class_count)
        
        i = 0
        for item in fmap:
            file_lines.append(self.format_line(item))
            i += 1

        i = 0
        for line in file_lines:
            fileoutput.write(line.lstrip())
            i += 1

        
        self.write_map()

    def format_headers(self, feature_count, class_count):
        """
        Formats the headers of the list to be written to the output
        file that will be converted to an arff file by the datautil.py
        utility

        param
        -----
        file_list: The list of strings to be written to the file - should
            be empty when used here
        feature_count: The number of features being used in the learning
            algorithm. E.G. if we're using the 4 nearest words, then this
            would equal 4
        class_count: the number of possible classes for the word, i.e. 
            the number of possible senses for a word. 
        """
        file_list = []

        file_list.append("# Feature Count\n")
        file_list.append(str(feature_count) + "\n")
        file_list.append("# Class Count \n")
        file_list.append(str(class_count)+ "\n")

        return file_list

    def format_line(self, line_map):
        """
        Takes a mapped line dictionary and formats it into a string
        to be written to an arff file. Writes multiple lines if the
        word contains multiple senses. 

        param
        -----
        line_map: A mapped line dictionary object in the format 
            created by the function map_line
        """
        line = []

        senses = self.map_sense(line_map['sense'])

        for sense in senses:
            # We don't need the word at the beginning of the line
            # at the moment
            #line.append(line_map['word'] + "." + line_map['pos'])
            line.append(line_map['coll_map'])
            line.append(sense)
            line.append("\n")

        return " ".join(line)

    def map_sense(self, sense):
        """
        Takes a sense string and returns a list of the senses that are
        contained within it, so with an input of "0 1 0 0 0" it will 
        return a list equal to ["2"], and for "0 1 0 1 0" it will 
        return ["2","4"]

        param
        -----
        sense: the string of senses that apply to this word in binary format
        """
        sense_list = sense.strip().split(" ")
        senses = []
        for i in range(len(sense_list)):
            if sense_list[i] == "1":
                senses.append(str(i + 1))

        if len(senses) == 0:
            senses.append("0")

        return senses

    def create_stop_words(self, file_map):
        """
        Takes a file map list object and creates stop words according to
	Zipf's law: F(rank) ~ 0.1 / rank. Given a threshold F(rank), any word
	satisfying F(rank_word) >= F(rank) will be considered as a stop word.
	For the frequency, the program uses IDF because it is proved to
	outperform when other frequencies such as TF are used. The threshold
        frequency F(rank) is defined as log(2/3) from our experiments on the
	given training data. Since F(r) = log(num_of_documents_the_word_appears 
	/ total_num_of_documents), for simplicity, we compare the following:
	    num_of_documents_the_word_appears >= threshold = tot_num_of_doc*2/3

        returns a hashtable whose keys are stop words

        param
        _____
        file_map: A list object created from self.map_file(...) which consists
            of line map dictionary objects. Each line map dictionary object
            should containt at least the key 'context' whose value is a string
        """
        word_counts = {}
        doc_count = 0.0

        for line_map in file_map:
            doc_count = doc_count + 1.0
            context = line_map['context']
            word_list = context.strip().lower().split(' ')
	    vocab = {}
            for word in word_list:
                if not vocab.has_key(word):
		    if word_counts.has_key(word):
                        word_counts[word] = word_counts[word] + 1.0
                    else:
                        word_counts[word] = 1.0
	        vocab[word] = 1

        stop_words = {}
        words = word_counts.keys()
        sigma = doc_count * 2.0 / 3.0

        for word in words:
            if word_counts[word] >= sigma:
                stop_words[word] = 1

        return stop_words

    def strip_file_map(self, file_map):
        """
        Takes a file map list object and eliminate stop words and any token that
        contains a non-alpha-numeric character such as (, ), ', etc except @.
        In our training data, the character @ is used to indicate the important
        words to be disambiguated thus critical to be kept in our file map object.

        returns a file map object stripped of trivial tokens and words

        param
        -----
        file_map: A list object created from self.map_file(...) which consists
            of line map dictionary objects. Each line map dictionary object
            should containt at least the key 'context' whose value is a string
        """
        stop_words = self.create_stop_words(file_map)

        file_map_stripped = []

        for line_map in file_map:
            if not stop_words.has_key(line_map['word']):
                file_map_stripped.append(self.strip_line_map(line_map, stop_words))

        return file_map_stripped

    def strip_line_map(self, line_map, stop_words):
        """
        Takes a line map object and a stop words object to strip the line map object
        of the stop words and any non-alpha-numeric tokens besides the tokens that
        contains '@', a special indicator for an important word.

        returns a line map stripped of trivial tokens and words

        param
        -----
        line_map: A dictionary containing WSD information such as word, pos, sense,
            context, coll, and coll_map
        stop_words: A dictionary containing stop words
        """
        context = line_map['context']

        context_stripped = self.strip_context(context, stop_words)
        line_map['context_stripped'] = context_stripped
        line_map['coll_map_stripped'] = self.map_coll(self.find_coll(context_stripped))

        return line_map

    def strip_context(self, context, stop_words):
        """
        Takes a context string and remove stop words and trivial non-alpha-numeric
        tokens from it.

        returns a modified context string stripped of trivial tokens
        -----
        context: A string
        stop_words: A dictionary containing stop words
        """
        stripped_word_list = []
        word_list = context.strip().split(' ')

        for word in word_list:
            if not stop_words.has_key(word):
                if word.isalnum() or '@' in word:
                    stripped_word_list.append(word)

        return ' '.join(stripped_word_list)
