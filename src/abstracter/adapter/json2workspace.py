"""
@file json2workspace.py

@brief Interface json and the Workspace.
"""

import json
import abstracter.workspace as wks


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
        text = json.loads(jsn)

        for parid, par in enumerate(text):
            for word in par:
                self.parse_word(word, parid)

    def parse_word(self, word, parid):
        wd = self.workspace.get_word(self, parid + "." + word["id"])
        if wd is None:
            if 'noun' in word["type"]:
                # Must test if word is head of chunk
                if word["tags"]["relations"]:
                    wd = wks.Entity()
                    for beginRepr, endRepr in word["tags"]["relations"]:
                        wd.add_reference((parid, beginRepr, endRepr))
                else:
                    wd = wks.Attribute()
            elif 'adj' in word["type"]:
                wd = wks.Attribute()
            elif 'verb' in word["type"]:
                # Verbs are very probably events or should be treated as such.
                wd = wks.Event()
