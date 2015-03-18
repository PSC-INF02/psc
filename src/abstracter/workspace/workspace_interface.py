class AbstractNetwork:
    """
    An abstract class containing the interface a network must have
    """

    def add_sentence(self):
        raise NotImplementedError("Should have implemented this")

    def get_sentence(self, sentID):
        raise NotImplementedError("Should have implemented this")

    def get_word(self, wid):
        raise NotImplementedError("Should have implemented this")
