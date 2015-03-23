#!/usr/bin/python3
"""@file crego_to_json.py
@brief Util to transform systran files into json objects.

"""

import re
import json


ALL_TAGS = ["det", "human", "location", "physub",
            "event", "abstract", "time", "sg",
            "oldtag", "modifies_another_noun",
            "governs_another_noun", "agent_of_verb",
            "has_apposition", "modified_by_prep1", "nfw",
            "apposition_to", "dirobj", "govern", "governed_by",
            "dirobj_of", "modifies_right_head", "semantic_modifier_of",
            "modified_by_adj", "modified_on_left", "skip_end", "nb", "per",
            "present", "agent_of_action", "object_of_action", "object_of_verb",
            "skip_begin", "future", "antecedent_of_relpro", "antecedent",
            "indirobj_of", "perfect", "indirobj", "past", "closing_quote_ptr",
            "opening_quote_ptr", "modified_on_right", "infinitive",
            "modifies_left_head", "pl", "modified_by_adverb", "modifies",
            "linked_to_predicate", "superlative", "predadj_of", "governs_nonfinite",
            "nonfinite_governed_by", "progressive", "comparative", "previous_enum",
            "next_enum", "neg", "modified_by_prep2",
            "passive", "emphatic", "refl"]


# tous les tags qui donnent des relations (lient à un autre mot)
RELATIONS = ["agent_of_action", "agent_of_verb", "antecedent",
             "antecedent_of_relpro", "apposition_to", "closing_quote_ptr",
             "dirobj", "dirobj_of", "govern", "governed_by", "governs_another_noun",
             "governs_nonfinite", "has_apposition", "indirobj", "indirobj_of",
             "linked_to_predicate", "modified_by_adj", "modified_by_adverb",
             "modified_by_prep1", "modified_by_prep2", "modified_on_left",
             "modified_on_right", "modifies", "modifies_another_noun", "modifies_left_head",
             "modifies_right_head", "next_enum", "nonfinite_governed_by", "object_of_action",
             "object_of_verb", "opening_quote_ptr", "predadj_of", "previous_enum",
             "semantic_modifier_of", "skip_begin", "skip_end"]


# tous les tags qui valent soit 0 soit 1
OTHER = ["abstract", "comparative", "emphatic", "event", "future",
         "human", "infinitive", "location", "neg", "nfw", "passive",
         "past", "perfect", "physub", "pl", "present", "progressive",
         "refl", "sg", "superlative", "time"]


# tous les tags qu'on trouve sur des verbes
VERB_TAGS = ["agent_of_action", "agent_of_verb", "apposition_to", 
             "closing_quote_ptr", "dirobj", "dirobj_of", "emphatic", 
             "future", "govern", "governed_by", "governs_another_noun", 
             "governs_nonfinite", "has_apposition", "human", "indirobj", 
             "indirobj_of", "infinitive", "linked_to_predicate", 
             "modified_by_adj", "modified_by_adverb", "modified_by_prep1", 
             "modified_by_prep2", "modified_on_left", "modified_on_right", 
             "modifies", "modifies_another_noun", "modifies_left_head", 
             "modifies_right_head", "nb", "neg", "next_enum", "nfw", 
             "nonfinite_governed_by", "object_of_action", "object_of_verb", 
             "oldtag", "opening_quote_ptr", "passive", "past", "per", "perfect", 
             "predadj_of", "present", "previous_enum", "progressive", "refl", 
             "semantic_modifier_of", "skip_begin", "skip_end"]
# examples [["agent_of_action", "send"], ["agent_of_verb", "mean"], 
# ["apposition_to", "celebrate"], ["closing_quote_ptr", "mean"], 
# ["dirobj", "send"], ["dirobj_of", "unite"], ["emphatic", "make"], 
# ["future", "play"], ["govern", "send"], ["governed_by", "miss"], 
# ["governs_another_noun", "sign"], ["governs_nonfinite", "unite"], 
# ["has_apposition", "sing"], ["human", "let_x_us"], ["indirobj", "beat"], 
# ["indirobj_of", "pick"], ["infinitive", "reach"], ["linked_to_predicate", "feel"], 
# ["modified_by_adj", "beat"], ["modified_by_adverb", "avoid"], 
# ["modified_by_prep1", "send"], ["modified_by_prep2", "talk"], 
# ["modified_on_left", "score"], ["modified_on_right", "beat"], 
# ["modifies", "do_x_not"], ["modifies_another_noun", "roar"], 
# ["modifies_left_head", "reach"], ["modifies_right_head", "unite"], 
# ["nb", "send"], ["neg", "trust"], ["next_enum", "miss"], 
# ["nfw", "gamesLosing"], ["nonfinite_governed_by", "do"], 
# ["object_of_action", "send"], ["object_of_verb", "score"], 
# ["oldtag", "send"], ["opening_quote_ptr", "mean"], ["passive", "foul"], 
# ["past", "say"], ["per", "send"], ["perfect", "beat"], 
# ["predadj_of", "referee"], ["present", "send"], ["previous_enum", "get"], 
# ["progressive", "face"], ["refl", "get"], ["semantic_modifier_of", "avoid"], 
# ["skip_begin", "battle"], ["skip_end", "demand"]]


NOUN_TAGS = ["abstract", "agent_of_verb", "antecedent_of_relpro", 
             "apposition_to", "closing_quote_ptr", "det", "dirobj", 
             "dirobj_of", "event", "govern", "governs_another_noun", 
             "governs_nonfinite", "has_apposition", "human", "indirobj_of", 
             "location", "modified_by_adj", "modified_by_adverb", 
             "modified_by_prep1", "modified_by_prep2", "modified_on_left", 
             "modified_on_right", "modifies",
             "modifies_another_noun", "next_enum",
             "nfw", "object_of_action", "object_of_verb", "oldtag",
             "opening_quote_ptr", "physub", "pl", "predadj_of",
             "previous_enum", "sg", "skip_begin", "skip_end", "time"]
# examples [["abstract", "Tottenham"], ["agent_of_verb", "Sheffield_+_United"],
# ["antecedent_of_relpro", "final"], ["apposition_to", "Kane"],
# ["closing_quote_ptr", "world"], ["det", "Tottenham"], ["dirobj", "controversy"],
# ["dirobj_of", "aggregate"], ["event", "Tottenham"], ["govern", "controversy"],
# ["governs_another_noun", "beat"], ["governs_nonfinite", "need"],
# ["has_apposition", "Sheffield_+_United"], ["human", "Tottenham"],
# ["indirobj_of", "londoner"], ["location", "Tottenham"], ["modified_by_adj", "CupThe"],
# ["modified_by_adverb", "Wembley"], ["modified_by_prep1", "Sheffield_+_United"],
# ["modified_by_prep2", "fee"], ["modified_on_left", "CupThe"],
# ["modified_on_right", "Tottenham"], ["modifies", "extra_+_time"],
# ["modifies_another_noun", "Tottenham"], ["next_enum", "fan"],
# ["nfw", "CupThe"], ["object_of_action", "controversy"], ["object_of_verb", "side"],
# ["oldtag", "Tottenham"], ["opening_quote_ptr", "world"], ["physub", "Tottenham"],
# ["pl", "spur"], ["predadj_of", "thing"], ["previous_enum", "crowd"], ["sg", "Tottenham"],
# ["skip_begin", "stand"], ["skip_end", "CupThe"], ["time", "Tottenham"]]


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


def crego_to_json(file):
    data = []
    with open(file, "r") as f:
        for line in f:
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

                data.append({
                    "id": len(data),
                    "name": word_details[0],
                    "norm": word_details[1],
                    "type": word_details[2],
                    "tags": tags
                })

    return data

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = crego_to_json(file)
    print(json.dumps(data))
