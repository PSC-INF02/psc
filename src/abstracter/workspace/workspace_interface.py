class AbstractNetwork:
    """
    An abstract class containing the interface a network must have
    """

    def add_word(self, parid, word):
        """
        Adds a word to the workspace

        @param parid the id of the paragraph the word belongs to
        @param word the word
        """
        raise NotImplementedError("Should have implemented this")

    def get_word(self, wid):
        """
        Get a word from the workspace and return null if it is absent
        """
        raise NotImplementedError("Should have implemented this")

    def get_or_add_word(self, wid):
        """
        Get a word from the workspace, creating it if absent
        """
