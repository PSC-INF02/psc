class AbstractWord:
    """
    An abstract class containing the interface a node in the network must have
    """

    def __init__(self, id):
        self.id = id  # The id in the workspace

    def addLemna(self, lemna):
        """
        Adds a lemna (in normalized form) to the word
        Args:
            lemna: the lemna (string) to add
        """
        raise NotImplementedError("Should have implemented this")

    def setType(self, wType):
        """
        Set the type of the word
        Args:
            wType: the type of the word
        """
        raise NotImplementedError("Should have implemented this")

    def addRelationTo(self, relation_type, dest):
        """
        Add a relation between this word and another

        Args:
            relation_type: guess...
            dest: guess too...
        this docstring is really useless
        """
        raise NotImplementedError("Should have implemented this")
