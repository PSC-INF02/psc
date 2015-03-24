#!/usr/bin/python3
"""
@file systran_parser.py
@brief Util to transform systran files into json objects.
"""

import re
import json


TAGS_INFO = {
        "abstract": {"keep": True, "cor": "ABSTRACT", "is_rel": False},
        "agent_of_action": {"keep": True, "cor": "AGENT_OF_ACTION", "is_rel": True},
        "agent_of_verb": {"keep": True, "cor": "AGENT_OF_VERB", "is_rel": True},
        "antecedent": {"keep": True, "cor": "ANTECEDENT", "is_rel": True},
        "antecedent_of_relpro": {"keep": True, "cor": "ANTECEDENT_OF_RELPRO", "is_rel": True},
        "apposition_to": {"keep": True, "cor": "APPOSITION_TO", "is_rel": True},
        "closing_quote_ptr": {"keep": False, "cor": "CLOSING_QUOTE_PTR", "is_rel": True},
        "comparative": {"keep": True, "cor": "COMPARATIVE", "is_rel": False},
        "dirobj": {"keep": True, "cor": "DIROBJ", "is_rel": True},
        "dirobj_of": {"keep": True, "cor": "DIROBJ_OF", "is_rel": True},
        "emphatic": {"keep": False, "cor": "EMPHATIC", "is_rel": False},
        "event": {"keep": True, "cor": "EVENT", "is_rel": False},
        "future": {"keep": True, "cor": "FUTURE", "is_rel": False},
        "govern": {"keep": True, "cor": "GOVERN", "is_rel": True},
        "governed_by": {"keep": True, "cor": "GOVERNED_BY", "is_rel": True},
        "governs_another_noun": {"keep": True, "cor": "GOVERNS_ANOTHER_NOUN", "is_rel": True},
        "governs_nonfinite": {"keep": False, "cor": "GOVERNS_NONFINITE", "is_rel": True},
        "has_apposition": {"keep": True, "cor": "HAS_APPOSITION", "is_rel": True},
        "human": {"keep": True, "cor": "HUMAN", "is_rel": False},
        "indirobj": {"keep": True, "cor": "INDIROBJ", "is_rel": True},
        "indirobj_of": {"keep": True, "cor": "INDIROBJ_OF", "is_rel": True},
        "infinitive": {"keep": True, "cor": "INFINITIVE", "is_rel": False},
        "linked_to_predicate": {"keep": False, "cor": "LINKED_TO_PREDICATE", "is_rel": True},
        "location": {"keep": False, "cor": "LOCATION", "is_rel": False},
        "modified_by_adj": {"keep": True, "cor": "MODIFIED_BY_ADJ", "is_rel": True},
        "modified_by_adverb": {"keep": True, "cor": "MODIFIED_BY_ADVERB", "is_rel": True},
        "modified_by_prep1": {"keep": True, "cor": "MODIFIED_BY_PREP1", "is_rel": True},
        "modified_by_prep2": {"keep": True, "cor": "MODIFIED_BY_PREP2", "is_rel": True},
        "modified_on_left": {"keep": True, "cor": "MODIFIED_ON_LEFT", "is_rel": True},
        "modified_on_right": {"keep": True, "cor": "MODIFIED_ON_RIGHT", "is_rel": True},
        "modifies": {"keep": True, "cor": "MODIFIES", "is_rel": True},
        "modifies_another_noun": {"keep": True, "cor": "MODIFIES_ANOTHER_NOUN", "is_rel": True},
        "modifies_left_head": {"keep": True, "cor": "MODIFIES_LEFT_HEAD", "is_rel": True},
        "modifies_right_head": {"keep": True, "cor": "MODIFIES_RIGHT_HEAD", "is_rel": True},
        "neg": {"keep": False, "cor": "NEG", "is_rel": False},
        "next_enum": {"keep": False, "cor": "NEXT_ENUM", "is_rel": True},
        "nfw": {"keep": True, "cor": "NFW", "is_rel": False},
        "nonfinite_governed_by": {"keep": False, "cor": "NONFINITE_GOVERNED_BY", "is_rel": True},
        "object_of_action": {"keep": True, "cor": "OBJECT_OF_ACTION", "is_rel": True},
        "object_of_verb": {"keep": True, "cor": "OBJECT_OF_VERB", "is_rel": True},
        "opening_quote_ptr": {"keep": False, "cor": "OPENING_QUOTE_PTR", "is_rel": True},
        "passive": {"keep": True, "cor": "PASSIVE", "is_rel": False},
        "past": {"keep": True, "cor": "PAST", "is_rel": False},
        "perfect": {"keep": True, "cor": "PERFECT", "is_rel": False},
        "physub": {"keep": False, "cor": "PHYSUB", "is_rel": False},
        "pl": {"keep": True, "cor": "PL", "is_rel": False},
        "predadj_of": {"keep": True, "cor": "PREDADJ_OF", "is_rel": True},
        "present": {"keep": True, "cor": "PRESENT", "is_rel": False},
        "previous_enum": {"keep": False, "cor": "PREVIOUS_ENUM", "is_rel": True},
        "progressive": {"keep": True, "cor": "PROGRESSIVE", "is_rel": False},
        "refl": {"keep": False, "cor": "REFL", "is_rel": False},
        "semantic_modifier_of": {"keep": True, "cor": "SEMANTIC_MODIFIER_OF", "is_rel": True},
        "sg": {"keep": True, "cor": "SG", "is_rel": False},
        "skip_begin": {"keep": False, "cor": "SKIP_BEGIN", "is_rel": True},
        "skip_end": {"keep": False, "cor": "SKIP_END", "is_rel": True},
        "superlative": {"keep": True, "cor": "SUPERLATIVE", "is_rel": False},
        "time": {"keep": True, "cor": "TIME", "is_rel": False},
}


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

TYPES = ["adj", "adv", "adv_x_aux:plain",
         "adv_x_det", "aux:inf", "aux:pastpart",
         "aux:plain", "aux:plain_x_adv", "aux:plain_x_aux:inf",
         "aux:plain_x_aux:pastpart", "aux:plain_x_aux:plain",
         "aux:prespart", "conj", "det", "intj", "noun:acronym",
         "noun:acronym_x_adv", "noun:acronym_x_punct",
         "noun:common", "noun:propernoun", "numeric",
         "numeric_x_punct", "prep", "prep_x_det", "pron",
         "pron_x_aux:plain", "prtcl", "punct", "symb",
         "verb:inf", "verb:pastpart", "verb:plain", "verb:plain_x_adv",
         "verb:plain_x_pron", "verb:prespart"]


def parse_systran(file):
    data = []
    with open(file, "r") as f:
        for line in f:
            words = []
            line_text = []
            for word in line.split(" "):
                word_details = word.split("-|-")

                tags = {"relations": []}
                for t in word_details[3].split(";"):
                    r = re.match(r"(.+)=(.+)", t)
                    if r is not None:
                        v = r.group(2)
                        if v[0] == '@':
                            v = int(v[1:])
                        tags[r.group(1)] = v
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
                line_text.append(word_details[0])
            data.append({
                "id": len(data),
                "text": " ".join(line_text),
                "words": words
            })
    return data

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = parse_systran(file)
    print(json.dumps(data))
