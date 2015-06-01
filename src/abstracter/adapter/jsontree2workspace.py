"""
@file jsontree2workspace.py

@brief Interface between json trees and the Workspace.

Example :
@code
import abstracter.adapter.jsontree2workspace as j2w
import abstracter.workspace.workspace as workspace
import json
import abstracter.grammar.grammartree as gt

wks = workspace.Workspace()

with open("../../fichiers_parses/0.grammartree.json") as jfile:
    piloup = json.load(jfile, cls=gt.GrammarTreeDecoder)

blah = j2w.jsonTree2W(wks)
blah.parse_forest([], piloup, piloup)
@endcode

"""

import abstracter.workspace.workspace as wks
import abstracter.grammar.grammartree as gt


def debug(x):
    pass
    # print(x)


class jsonTree2W:
    """
    Interfaces the JSON Tree resulting from Systran's analysis
    with the workspace.
    """

    def __init__(self, workspace):
        self.workspace = workspace
        self.tags = {
            "subject_of": [
                "AGENT_OF_VERB",
                "AGENT_OF_ACTION",
            ],
            "object_of": ["OBJECT_OF_ACTION", "INDIROBJ"],
            "modified_by": [
                "MODIFIED_BY_ADVERB",
                "MODIFIED_BY_PREP1",
                "MODIFIED_BY_PREP2",
                "MODIFIED_BY_PREP3",
                "MODIFIED_BY_ADj",
                "MODIFIED_ON_LEFT",
                "MODIFIED_ON_RIGHT",

            ],
            "attribute_of": [
                "MODIFIES_ANOTHER_NOUN",
                "MODIFIES_LEFT_HEAD",
                "MODIFIES_RIGHT_HEAD",
            ],
            "various": [
                "LINKED_TO_PREDICATE",
            ],
        }

        self.parsers = {
            "noun": self.parse_noun,
            "adj": self.parse_adj,
            "verb": self.parse_event,
            "aux": self.parse_event,
            "other": self.parse_other,
            "paragraph": self.parse_word_group,
            "sentence": self.parse_word_group,
            "word_group": self.parse_word_group,
        }

    def deserialize_id(self, serial):
        return [int(x) for x in serial.split(":")[0].split(", ")]

    def find_relations(self, tags):
        relations = []
        for lbl, val in tags.items():
            for rel_type, rels in self.tags.items():
                if lbl in rels:
                    relations.append((rel_type, val))
        return relations

    def parse_noun(self, id, noun):
        wd = wks.Entity(id, name=noun.contents["text"],
                        tags=noun.contents)
        return wd

    def parse_event(self, id, verb):
        wd = wks.Event(id, name=verb.contents["text"], tags=verb.contents)
        return wd

    def parse_adj(self, id, adj):
        wd = wks.Attribute(id, name=adj.contents["text"], tags=adj.contents)
        return wd

    def parse_other(self, id, word):
        wd = wks.Syntagm(id, name=word.contents["text"], tags=word.contents)
        return wd

    def parse_word_group(self, id, wg):
        # name = if "text" in wg.contents then wg.contents["text"] else
        name = wg.contents["text"] if "text" in wg.contents else ""
        wd = wks.Syntagm(id, name=name, tags=wg.contents)
        return wd

    def add_tags(self, word, contents):
        if "tags" in contents:
            for tag, val in contents["tags"].items():
                word.add_tag(tag, val)

    def get_nature(self, contents):
        if "kind" not in contents:
            return "word_group"
        for nature in self.parsers:
            if nature in contents['kind']:
                return nature
        return "other"

    def parse_node(self, parid, node):
        id = parid.copy()
        id.append(node.id)
        if id is None:
            id = []
        if type(node) == gt.GrammarTree:
            nb_childs = len(node.children)
            self.parse_forest(id, node.children, node)
        else:
            nb_childs = 0
        wd = self.parsers[self.get_nature(node.contents)](id, node)
        wd.set_number_children(nb_childs)
        self.add_tags(wd, node.contents)
        wd.add_relations(self.find_relations(node.contents))
        if wd is None:
            debug("word " + str(id) + " is None !")
        self.workspace.add_node(id, node=wd)
        debug("word " + str(id) + " added to workspace")

    def parse_forest(self, id, forest, parent):
        for son in forest:
            self.parse_node(id, son)
