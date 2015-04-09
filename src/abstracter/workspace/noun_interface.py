import word_interface


class AbstractNoun(word_interface.AbstractWord):
    def addRepresentant(self, rawString, attributes):
        """
        Add a representant to the noun
        Args:
            rawString: the string in the sentence
                representing the noun (whole chunk)
            attributes: a list of attributes assiociated with the representant
        """
        raise NotImplementedError("Fuck the world")
