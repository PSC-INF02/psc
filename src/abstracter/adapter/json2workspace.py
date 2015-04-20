"""
@file json2workspace.py

@brief Interface json and the Workspace.
"""

import abstracter.workspace.workspace as wks


class Json2W:
    """
    @class Json2W
    A utility class to convert json objects into workspace entities
    """

    def __init__(self, workspace):
        self.workspace = workspace

    def parse(self, jsn):
        """
        Parse a json tree and fills the workspace

        @param jsn The json tree to parse
        @param workspace Current workspace
        """
        text = jsn  # json.loads(jsn)

        #  for parid, par in enumerate(text):
        for sent in text:
            for word in sent["words"]:
                self.parse_word(word, sent["id"])

    def parse_noun(self, word, parid):
        wd = wks.Entity()
        wd.add_reference((parid, word["id"]), (parid, word["id"]))
        for beginRepr, endRepr in word["tags"]["relations"]:
            for i in range(beginRepr, endRepr):
                if not (parid, i) in wd.get_attributes():
                    wd.add_attribute((parid, i))

    def parse_adj(self, word, parid):
        return wks.Attribute(word["norm"])

    def parse_event(self, word, parid):
        # Verbs are very probably events or should be treated as such.
        dests = []
        for tag in ["OBJECT_OF_ACTION", "INDIROBJ"]:
            if tag in word["tags"]:
                dests.append((parid, word["tags"][tag]))
        return wks.Event((parid, word["tags"]["AGENT_OF_ACTION"]), dests)

    def parse_word(self, word, parid):
        wd = self.workspace.get_word(parid, word["id"])
        if wd is None:
            if 'noun' in word["type"]:
                wd = self.parse_noun(word, parid)
            elif 'adj' in word["type"]:
                wd = self.parse_adj(word, parid)
            elif 'verb' in word["type"]:
                wd = self.parse_event(word, parid)
            self.workspace.add_word(parid, wd)
