class abstractNetwork:
    """
    An abstract class containing the interface a network must have
    """

    def addSentence(self):
        raise NotImplementedError("Should have implemented this")

    def getSentence(self, sentID):
        raise NotImplementedError("Should have implemented this")

    def getWord(self, wid):
        raise NotImplementedError("Should have implemented this")
