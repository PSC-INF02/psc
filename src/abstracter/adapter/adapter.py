"""@file adapter.py

"""


class Adapter:
    """
    @class Adapter

    Takes an article analyzed by systran
    and pours elements from it into a workspace.

    To use it :
    @code
    adapter.parse(filename, workspace)
    @endcode
    """

    def parse(self, filename, workspace):
        """
        Parses a syntactic tree (systran format) and fills workspace
        given as argument with new information.

        @param filename Name of the file to parse.
        @param workspace Current workspace.
        """
        f = open(filename, 'r')
        for line in f:
            # Each line is a sentence
            parsedSent = []
            words = line.split(' ')
            for word in words:
                # Spaces serve as a delimiter for words in a sentence
                parsedSent.append(self.parseWord(word, workspace, words))
            workspace.add_sentence(parsedSent)

    def parseWord(self, word, workspace, words):
        """
        Takes a cursory glance at whatever information is stored in the word
        (systran format) and returns it as a dictionary

        @param word A word in the text, given with much
        information (-|- separator).
        @param workspace Current workspace.

        @return A dict representing all information about the word.
        """
        wordStatus = word.split('-|-')
        wordCar = {}

        wordCar['word'] = wordStatus.pop(0)
        wordCar['lemma'] = wordStatus.pop(0)
        wordCar['nature'] = wordStatus.pop(0)

        '''
         Now there are two possibilities :
         - The name is a name, and I need to see whether it's a
             head of chunk or just a part
        - it's an adjective / verb or such and I need to make it
             an attribute or an event and to gather some more information.
        '''
        # Getting features and relations to other words in the sentence
        # (just in case)

        features = wordStatus.pop(0).split(';')

        if 'noun' in wordCar['nature']:
            '''a noun can be either a head of chunk or part of a chunk ;
            if the latter, it is more an attribute than an actual entity.
        So, checking if the name is a head of chunk, and if so adding the whole
        chunk, otherwise adding it as an attribute
        '''
        if self.isHeadOfChunk(features):
            chunkName = self.getChunkName(features, words)
        # else:
        #    pass
        else:
            '''
            For now I'll stay simple and just ignore everything
            until the relations in the sentence ;
            there might be some useful info in those features though.
            '''
            while 'oldtag' not in features.pop():
                pass

            if 'adj' in wordCar['nature']:
                # Seek some particular tag that should be useful, add node
                pass

            if 'verb' in wordCar['nature']:
                # Seek some particular tag that should be useful, add node
                pass

        return wordCar

    def getChunkName(features, words):
        """
        Gets a whole chunk of sentence as the longest in the features list

        @param features Features of the word under study, containing
        (among other things) chunks of which it is the head
        @param words Array of all the words in the sentence

        @return Longest chunk as a string
        """
        longestChunk = [0, 0]

        for feature in features:
            if feature[0].isdigit():
                # First symbol of feature is a digit : those are chunks, in the format chunkStart_@_chunkEnd
                currentChunk = feature.split("_@_")
                if currentChunk[1] - currentChunk[0] > longestChunk[1] - longestChunk[0]:
                    longestChunk[0] = currentChunk[0]
                    longestChunk[1] = currentChunk[1]
        chunkName = ""
        for word in words[longestChunk[0]:longestChunk[1]]:
            chunkName.append(word.split("-|-").pop())
            chunkName.append(" ")

        return chunkName

    def isHeadOfChunk(features):
        """
        Checks whether a word having those features (in Systran sense) is a head of chunk.

        @param features Features of the word to study

        @return True if the word is head.
        """
        test = False
        for feature in features:
            if feature[0].isdigit():
                test = True

        return test
