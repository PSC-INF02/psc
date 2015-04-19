class Workspace:
    """
    THE Workspace
    """

    def __init__(self):
        self.words = {}

    def add_word(self, parid, word=None):
        if word is None:
            raise RuntimeError("The word must not be null")
        else:
            wid = parid + "." + word["id"]
            self.words[wid] = word
            return wid

    def get_word(self, wid):
        return self.words[wid]
