
class adapter:
    """
    A class that takes an article analyzed by systran
    and pours elements from it into a workspace
    Use it with
    adapter.parse(filename, workspace);
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
                parsedSent.append(self.parseWord(word, workspace))
            workspace.addSentence(parsedSent)

    def parseWord(self, word, workspace):
        """
        Takes a cursory glance at whatever information is stored in the word
        (systran format) and returns it as a dictionary

        @param word A word in the text, given with much information (-|- separator).
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
             - the name is just a name and I can push it in the workspace as is
             - it's an adjective / verb or such and I need to make it
             an attribute or an event and to gather some more information.
        '''

        if 'noun' in wordCar['nature']:
            # I'll read doc to see what I can get into a node
            pass

        else:

            # Getting features and relations to other words in the sentence
            # (just in case)

            features = wordStatus.pop(0).split(';')

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
