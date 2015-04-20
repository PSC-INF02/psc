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
        self.tags_event_dest = ["OBJECT_OF_ACTION", "INDIROBJ"]
        self.tags_entity_attributes = [
            "MODIFIED_BY_ADVERB",
            "MODIFIED_BY_PREP1",
            "MODIFIED_BY_PREP2",
            "MODIFIED_BY_PREP3",
            "MODIFIED_BY_ADj",
            "GOVERNS_ANOTHER_NOUN"
        ]

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
        for tag in self.tags_entity_attributes:
            if tag in word["tags"]:
                wd.add_attribute((parid, word["tags"][tag]))
        for representant in word["tags"]["relations"]:
            wd.add_reference(representant)

    def parse_adj(self, word, parid):
        return wks.Attribute(word["norm"])

    def parse_event(self, word, parid):
        # Verbs are very probably events or should be treated as such.
        dests = []
        for tag in self.tags_event_dest:
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
