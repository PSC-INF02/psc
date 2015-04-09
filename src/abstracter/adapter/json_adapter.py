"""
@file json_adapter.py
"""

import json
# from abstracter.workspace.interface.workspaceInterface import abstractNetwork


class JsonAdapter:
    """
    Interface between json and the workspace
    """

    def __init__(self, workspace):
        self.workspace = workspace

    def parse(self, jsonStream):
        """
        Parse the json as argument and fills the workspace
        Args:
            jsonStream: A json representing a text
            workspace: The workspace to fill
        """

        text = json.loads(jsonStream)

        for par in text:
            # First we put every element into the workspace
            for word in par:
                word['wId'] = self.workspace.add_word()
            # Then we etablish links between entities
            for word in par:
                self.parse_word(word, text)

    def parse_word(self, word, text):
        pass
        # TODO

    def parse_noun(self, word, text):
        pass
        # TODO
