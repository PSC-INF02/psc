"""
@file jsontree2workspace.py

@brief Interface between json trees and the Workspace.
"""

import abstracter.workspace.workspace as wks
import abstracter.grammar.grammartree as gt


def debug(x):
    print(x)


class jsonTree2W:

    def __init__(self, workspace):
        self.workspace = workspace
        self.tags_subject = [
            "AGENT_OF_VERB",
            "AGENT_OF_ACTION",
        ]
        self.tags_event_dest = ["OBJECT_OF_ACTION", "INDIROBJ"]
        self.tags_entity_attributes = [
            "MODIFIED_BY_ADVERB",
            "MODIFIED_BY_PREP1",
            "MODIFIED_BY_PREP2",
            "MODIFIED_BY_PREP3",
            "MODIFIED_BY_ADj",
            # "GOVERNS_ANOTHER_NOUN"
        ]

    def deserialize_id(self, serial):
        return [int(x) for x in serial.split(":")[0].split(", ")]

    def find_relations(self, tags):
        relations = {}
        for lbl, val in tags.items():
            if lbl in self.tags_subject:
                relations["subject_of"] = self.deserialize_id(val)
            elif lbl in self.tags_event_dest:
                relations["object_of"] = self.deserialize_id(val)
            elif lbl in self.tags_entity_attributes:
                relations["modified_by"] = self.deserialize_id(val)
        return relations

    def parse_noun(self, id, noun):
        wd = wks.Entity(id, noun)
        return wd

    def parse_event(self, id, verb):
        wd = wks.Event(id, verb)
        return wd

    def parse_adj(self, id, adj):
        wd = wks.Attribute(id, adj)
        return wd

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
        if 'noun' in node.contents["kind"]:
            wd = self.parse_noun(id, node)
        elif 'adj' in node.contents["kind"]:
            wd = self.parse_adj(id, node)
        else:
            wd = self.parse_event(id, node)
        wd.set_number_children(nb_childs)
        if "tags" in node.contents:
            for tag, val in node.contents["tags"].items():
                wd.add_tag(tag, val)
        if wd is None:
            debug("word " + str(id) + " is None !")
        self.workspace.add_node(id, node=wd)
        debug("word " + str(id) + " added to workspace")

    def parse_forest(self, id, forest, parent):
        for son in forest:
            self.parse_node(id, son)
