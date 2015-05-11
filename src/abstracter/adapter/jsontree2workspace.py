"""
@file jsontree2workspace.py

@brief Interface between json trees and the Workspace.
"""

import abstracter.workspace.workspace as wks


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

    def parse_noun(self, noun):
        wd = wks.Entity(noun)
        return wd

    def parse_verb(self, verb):
        wd = wks.Event(verb)
        return wd

    def parse_adj(self, adj):
        wd = wks.Attribute(adj)
        return wd

    def parse_node(self, parid, node):
        id = parid.append(node["id"])
        nb_childs = len(node["children"])
        self.parse_forest(id, node["children"])
        if 'noun' in node["kind"]:
            wd = self.parse_noun(node)
        elif 'adj' in node["kind"]:
            wd = self.parse_adj(node)
        else:
            wd = self.parse_event(node)
        wd.set_number_children(nb_childs)
        if "tags" in node:
            for tag, val in node["tags"]:
                wd.add_tag(tag, val)
        self.workspace.add_node(wd)

    def parse_forest(self, id, forest, parent):
        for son in forest:
            if parent is not None:
                son["tags"]["parent"] = parent
            self.parse_node(id, son)
