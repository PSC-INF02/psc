from abstracter.workspace.workspaceInterface import abstractNetwork
from collections import Counter


class statsPseudoWorkspace(abstractNetwork):
    """
    A pseudo workspace used only for statistic calculations
    """

    def __init__(self):
        self.__interndict__ = {
            'noun': Counter(),
            'verb': Counter(),
            'adj': Counter(),
            'other': Counter(),
        }

    def __getitem__(self, item):
        return self.__interndict__[item]

    def addSentence(self, sentence):
        for word in sentence:
            self.addWord(word)

    def addWord(self, word):
        if 'noun' in word['nature']:
            typeOfWord = self['noun']
        elif 'verb' in word['nature']:
            typeOfWord = self['verb']
        elif 'adj' in word['nature']:
            typeOfWord = self['adj']
        else:
            typeOfWord = self['other']
        typeOfWord[word['lemma']] += 1
