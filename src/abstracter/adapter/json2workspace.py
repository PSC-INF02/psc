"""
@file json2workspace.py

@brief Interface json and the Workspace.
"""

import json
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

    def parse_word(self, word, parid):
        wd = self.workspace.get_word(parid,word["id"])
        if wd is None:
            if 'noun' in word["type"]:
                wd = wks.Entity()
                wd.add_reference((parid, word["id"]), (parid, word["id"]))
                for beginRepr, endRepr in word["tags"]["relations"]:
                    for i in range(beginRepr, endRepr):
                        if not (parid,i) in wd.get_attributes():
			   wd.add_attribute((parid, i))
            elif 'adj' in word["type"]:
                wd = wks.Attribute(word["norm"])
            elif 'verb' in word["type"]:
                # Verbs are very probably events or should be treated as such.
                # wd = wks.Event()
                pass
