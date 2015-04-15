"""
@file json2workspace.py
@bref interface json and the workspace
"""

import json
import abstracter.workspace as wks


class Json2W:
    """
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

    def parse_world(self, word, parid):
        wd = self.workspace.get_word(self, parid + "." + word["id"])
        if wd is None:
            if 'noun' in word["type"]:
                wd = wks.Entity()
                for beginRepr, endRepr in word["tags"]["relations"]:
                    wd.add_reference((parid, beginRepr, endRepr))
            elif 'adj' in word["type"]:
                wd = wks.Attribute()
            else:
                # TODO
                wd = wks.Attribute()
