#!/usr/bin/python3
"""
@file systran_parser.py
@brief Transform systran files into json objects.
"""

import re
import json
from abstracter.grammar.utils import TAGS_INFO


TAGS_MAP = {
    "abstract": "ABSTRACT",
    "agent_of_action": "AGENT_OF_ACTION",
    "agent_of_verb": "AGENT_OF_VERB",
    "antecedent": "ANTECEDENT",
    "antecedent_of_relpro": "ANTECEDENT_OF_RELPRO",
    "apposition_to": "APPOSITION_TO",
    # "closing_quote_ptr": "CLOSING_QUOTE_PTR",
    "comparative": "COMPARATIVE",
    "det": "DET",
    "dirobj": "DIROBJ",
    "dirobj_of": "DIROBJ_OF",
    # "emphatic": "EMPHATIC",
    "event": "EVENT",
    "future": "FUTURE",
    "govern": "GOVERN",
    "governed_by": "GOVERNED_BY",
    "governs_another_noun": "GOVERNS_ANOTHER_NOUN",
    "governs_nonfinite": "GOVERNS_NONFINITE",
    "has_apposition": "HAS_APPOSITION",
    "human": "HUMAN",
    "indirobj": "INDIROBJ",
    "indirobj_of": "INDIROBJ_OF",
    "infinitive": "INFINITIVE",
    "linked_to_predicate": "LINKED_TO_PREDICATE",
    "location": "LOCATION",
    "modified_by_adj": "MODIFIED_BY_ADJ",
    "modified_by_adverb": "MODIFIED_BY_ADVERB",
    "modified_by_prep1": "MODIFIED_BY_PREP1",
    "modified_by_prep2": "MODIFIED_BY_PREP2",
    "modified_on_left": "MODIFIED_ON_LEFT",
    "modified_on_right": "MODIFIED_ON_RIGHT",
    "modifies": "MODIFIES",
    "modifies_another_noun": "MODIFIES_ANOTHER_NOUN",
    "modifies_left_head": "MODIFIES_LEFT_HEAD",
    "modifies_right_head": "MODIFIES_RIGHT_HEAD",
    # "nb": "NB",
    "neg": "NEG",
    # "next_enum": "NEXT_ENUM",
    # "nfw": "NFW",
    "nonfinite_governed_by": "NONFINITE_GOVERNED_BY",
    "object_of_action": "OBJECT_OF_ACTION",
    "object_of_verb": "OBJECT_OF_VERB",
    # "oldtag": "OLDTAG",
    # "opening_quote_ptr": "OPENING_QUOTE_PTR",
    "passive": "PASSIVE",
    "past": "PAST",
    # "per": "PER",
    "perfect": "PERFECT",
    "physub": "PHYSUB",
    "pl": "PL",
    "predadj_of": "PREDADJ_OF",
    "present": "PRESENT",
    # "previous_enum": "PREVIOUS_ENUM",
    "progressive": "PROGRESSIVE",
    # "refl": "REFL",
    "semantic_modifier_of": "SEMANTIC_MODIFIER_OF",
    "sg": "SG",
    # "skip_begin": "SKIP_BEGIN",
    # "skip_end": "SKIP_END",
    "superlative": "SUPERLATIVE",
    "time": "TIME"
}


def parse_systran(file):
    data = []
    with open(file, "r") as f:
        for paragraph in f:
            words = []
            paragraph_text = []
            for word in paragraph.split(" "):
                word_details = word.split("-|-")
                if len(word_details) != 4:
                    words.append({
                        "id": len(words),
                        "error": "error",
                        "word": word
                    })
                    continue

                tags = {"relations": []}
                for t in word_details[3].split(";"):
                    r = re.match(r"(.+)=(.+)", t)
                    if r is not None:
                        tag = r.group(1)
                        v = r.group(2)

                        if tag == "nb" or tag == "per":
                            if "PERSONS" not in tags:
                                tags["PERSONS"] = []
                            tags["PERSONS"].append(v)

                        elif tag in TAGS_MAP:
                            tag = TAGS_MAP[tag]
                            tag_info = TAGS_INFO[tag]
                            if tag_info['type'] == "relation":
                                v = int(v[1:])
                            elif tag_info['type'] == "boolean":
                                v = bool(int(v))

                            tags[tag] = v

                    else:
                        tags["relations"].append(tuple(map(int, t.split("_@_"))))

                if "PERSONS" in tags:
                    persons = tags["PERSONS"]
                    nbs = persons[::2]
                    pers = [int(x[:-2]) for x in persons[1::2]]
                    tags["PERSONS"] = list(zip(pers, nbs))

                words.append({
                    "id": len(words),
                    "name": word_details[0],
                    "norm": word_details[1],
                    "type": word_details[2],
                    "tags": tags
                })
                paragraph_text.append(word_details[0])
            data.append({
                "id": len(data),
                "text": " ".join(paragraph_text),
                "words": words
            })
    return data


if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = parse_systran(file)
    print(json.dumps(data))
