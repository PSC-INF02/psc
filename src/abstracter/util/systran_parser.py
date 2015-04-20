#!/usr/bin/python3
"""
@file systran_parser.py
@brief Util to transform systran files into json objects.
"""

import re
import json


TAGS_INFO = {
    "abstract": {"id": "ABSTRACT", "type": "boolean"},
    "agent_of_action": {"id": "AGENT_OF_ACTION", "type": "relation"},
    "agent_of_verb": {"id": "AGENT_OF_VERB", "type": "relation"},
    "antecedent": {"id": "ANTECEDENT", "type": "relation"},
    "antecedent_of_relpro": {"id": "ANTECEDENT_OF_RELPRO", "type": "relation"},
    "apposition_to": {"id": "APPOSITION_TO", "type": "relation"},
    "closing_quote_ptr": {"id": "CLOSING_QUOTE_PTR", "type": "relation"},
    "comparative": {"id": "COMPARATIVE", "type": "boolean"},
    "det": {"id": "DET", "type": "unknown"},
    "dirobj": {"id": "DIROBJ", "type": "relation"},
    "dirobj_of": {"id": "DIROBJ_OF", "type": "relation"},
    "emphatic": {"id": "EMPHATIC", "type": "boolean"},
    "event": {"id": "EVENT", "type": "boolean"},
    "future": {"id": "FUTURE", "type": "boolean"},
    "govern": {"id": "GOVERN", "type": "relation"},
    "governed_by": {"id": "GOVERNED_BY", "type": "relation"},
    "governs_another_noun": {"id": "GOVERNS_ANOTHER_NOUN", "type": "relation"},
    "governs_nonfinite": {"id": "GOVERNS_NONFINITE", "type": "relation"},
    "has_apposition": {"id": "HAS_APPOSITION", "type": "relation"},
    "human": {"id": "HUMAN", "type": "boolean"},
    "indirobj": {"id": "INDIROBJ", "type": "relation"},
    "indirobj_of": {"id": "INDIROBJ_OF", "type": "relation"},
    "infinitive": {"id": "INFINITIVE", "type": "boolean"},
    "linked_to_predicate": {"id": "LINKED_TO_PREDICATE", "type": "relation"},
    "location": {"id": "LOCATION", "type": "boolean"},
    "modified_by_adj": {"id": "MODIFIED_BY_ADJ", "type": "relation"},
    "modified_by_adverb": {"id": "MODIFIED_BY_ADVERB", "type": "relation"},
    "modified_by_prep1": {"id": "MODIFIED_BY_PREP1", "type": "relation"},
    "modified_by_prep2": {"id": "MODIFIED_BY_PREP2", "type": "relation"},
    "modified_on_left": {"id": "MODIFIED_ON_LEFT", "type": "relation"},
    "modified_on_right": {"id": "MODIFIED_ON_RIGHT", "type": "relation"},
    "modifies": {"id": "MODIFIES", "type": "relation"},
    "modifies_another_noun": {"id": "MODIFIES_ANOTHER_NOUN", "type": "relation"},
    "modifies_left_head": {"id": "MODIFIES_LEFT_HEAD", "type": "relation"},
    "modifies_right_head": {"id": "MODIFIES_RIGHT_HEAD", "type": "relation"},
    "nb": {"id": "NB", "type": "unknown"},
    "neg": {"id": "NEG", "type": "boolean"},
    "next_enum": {"id": "NEXT_ENUM", "type": "relation"},
    "nfw": {"id": "NFW", "type": "boolean"},
    "nonfinite_governed_by": {"id": "NONFINITE_GOVERNED_BY", "type": "relation"},
    "object_of_action": {"id": "OBJECT_OF_ACTION", "type": "relation"},
    "object_of_verb": {"id": "OBJECT_OF_VERB", "type": "relation"},
    "oldtag": {"id": "OLDTAG", "type": "relation"},
    "opening_quote_ptr": {"id": "OPENING_QUOTE_PTR", "type": "relation"},
    "passive": {"id": "PASSIVE", "type": "boolean"},
    "past": {"id": "PAST", "type": "boolean"},
    "per": {"id": "PER", "type": "unknown"},
    "perfect": {"id": "PERFECT", "type": "boolean"},
    "physub": {"id": "PHYSUB", "type": "boolean"},
    "pl": {"id": "PL", "type": "boolean"},
    "predadj_of": {"id": "PREDADJ_OF", "type": "relation"},
    "present": {"id": "PRESENT", "type": "boolean"},
    "previous_enum": {"id": "PREVIOUS_ENUM", "type": "relation"},
    "progressive": {"id": "PROGRESSIVE", "type": "boolean"},
    "refl": {"id": "REFL", "type": "boolean"},
    "semantic_modifier_of": {"id": "SEMANTIC_MODIFIER_OF", "type": "relation"},
    "sg": {"id": "SG", "type": "boolean"},
    "skip_begin": {"id": "SKIP_BEGIN", "type": "relation"},
    "skip_end": {"id": "SKIP_END", "type": "relation"},
    "superlative": {"id": "SUPERLATIVE", "type": "boolean"},
    "time": {"id": "TIME", "type": "boolean"}
}

KEPT_TAGS = set([
    "abstract",
    "agent_of_action",
    "agent_of_verb",
    "antecedent",
    "antecedent_of_relpro",
    "apposition_to",
    "comparative",
    "det",
    "dirobj",
    "dirobj_of",
    "event",
    "future",
    "govern",
    "governed_by",
    "governs_another_noun",
    "has_apposition",
    "human",
    "indirobj",
    "indirobj_of",
    "infinitive",
    "modified_by_adj",
    "modified_by_adverb",
    "modified_by_prep1",
    "modified_by_prep2",
    "modified_on_left",
    "modified_on_right",
    "modifies",
    "modifies_another_noun",
    "modifies_left_head",
    "modifies_right_head",
    "neg",
    "nfw",
    "object_of_action",
    "object_of_verb",
    "passive",
    "past",
    "perfect",
    "pl",
    "predadj_of",
    "present",
    "progressive",
    "semantic_modifier_of",
    "sg",
    "superlative",
    "time"
])

# ALL_TYPES_EXAMPLES = {"aux:plain": "will", "intj": "no", "verb:inf": "reach",
#                       "prep_x_det": "with_x_the", "noun:acronym_x_punct": "a._x_.",
#                       "prtcl": "to", "adj": "capital", "noun:propernoun": "Tottenham",
#                       "adv_x_det": "a_+_little_x_more", "aux:plain_x_aux:inf": "would_x_have",
#                       "verb:plain_x_adv": "do_x_not", "symb": "'", "verb:pastpart": "avoid",
#                       "verb:prespart": "give", "aux:plain_x_adv": "do_x_not",
#                       "noun:acronym": "cup.Christian", "aux:pastpart": "be",
#                       "det": "the", "verb:plain": "send", "numeric_x_punct": "7._x_.",
#                       "pron": "who", "conj": "and", "aux:plain_x_aux:pastpart": "have_x_be",
#                       "aux:prespart": "have", "numeric": "3-2", "prep": "on",
#                       "noun:common": "beat", "verb:plain_x_pron": "let_x_us",
#                       "pron_x_aux:plain": "that_x_be", "punct": ",",
#                       "aux:inf": "have", "adv": "on_+_March_+_1",
#                       "adv_x_aux:plain": "there_x_be",
#                       "aux:plain_x_aux:plain": "have_x_be", "noun:acronym_x_adv": "1-1did_x_not"}

# TAGS = {
#     "abstract": {
#         "type": "boolean",
#         "modifies": ["noun"]
#     }
# }

def parse_systran(file):
    data = []
    with open(file, "r") as f:
        for paragraph in f:
            words = []
            paragraph_text = []
            for word in paragraph.split(" "):
                word_details = word.split("-|-")

                tags = {"relations": []}
                for t in word_details[3].split(";"):
                    r = re.match(r"(.+)=(.+)", t)
                    if r is not None:
                        tag = r.group(1)
                        v = r.group(2)

                        if tag in KEPT_TAGS:
                            tag = TAGS_INFO[tag]
                            if tag['type'] == "relation":
                                v = int(v[1:])
                            elif tag['type'] == "boolean":
                                v = bool(int(v))

                            tags[tag['id']] = v

                    else:
                        x = map(int, t.split("_@_"))
                        tags["relations"].append(tuple(x))

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
