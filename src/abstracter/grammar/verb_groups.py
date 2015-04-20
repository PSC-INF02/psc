"""@file verb_groups.py

Possibility to find verb groups inside a text.

@code
from abstracter.grammar.systran_parser import parse_systran
from abstracter.grammar.verb_groups import get_verb_groups, print_verb_groups

sents = parse_systran("../systran/3.clean.wsd.linear")
nps = get_verb_groups(sents)
print(nps)
print_verb_groups(sents)
@endcode
"""

from abstracter.grammar.utils import VERB_GROUPS_TYPES, has_tag_in, has_type_in, MASTER_VERB_TAGS, get_word, TO_BE_ADDED_VB, TO_ADD_VB


def get_verb_groups(sentences):
    """
    @return A list of dicts. Each one corresponds to a sentence and
    has the following form :
    {(0, 0): [], (0, 8): [(0, 6), (0, 7)]}
    Each id is a two-tuple, corresponding to a word
    (sentence id and word id in the sentence).
    Thus, the information of the tuple's first element is redundant
    with the position of the dict in the resulting list.
    This is more practical.

    @see abstracter.util.systran_parser.py
    """
    res_list = []
    # treat each sentence separately
    for sent in sentences:
        res = {}
        sent_id = sent["id"]
        for word in sent["words"]:
            term_id = (sent_id, word["id"])
            if (word
               and word["type"] in VERB_GROUPS_TYPES
               and has_tag_in(word, MASTER_VERB_TAGS)):
                res[term_id] = []
                # add related words
                for tag in TO_ADD_VB:
                    temp = (sent_id, word["tags"].get(tag, None))
                    if (temp and temp != term_id
                       and temp not in res[term_id]
                       and get_word(temp, sentences)
                       and get_word(temp, sentences)["type"] in VERB_GROUPS_TYPES):
                        res[term_id].append(temp)

        # ckeck all words in the phrase, in case we have forgotten one
        for word in sent["words"]:
            term_id = (sent_id, word["id"])
            if term_id not in res and has_type_in(word, VERB_GROUPS_TYPES):
                for tag in TO_BE_ADDED_VB:
                    temp = (sent_id, word["tags"].get(tag, None))
                    if temp in res:
                        if temp != term_id and term_id not in res[temp]:
                            res[temp].append(term_id)
        for term_id in res:
            res[term_id].sort()
        res_list.append(res)
    return res_list


def refactor_vps(vps):
    """

    """
    res_dict = {}
    for d in vps:
        for k in d:
            res_dict[k] = d[k]
    return res_dict


def print_verb_groups(sentences):
    """
    Utilitary to check if we've obtained the proper verb groups.

    This allows the user to run some tests.

    @see get_noun_phrases
    """
    vps = get_verb_groups(sentences)
    for nps in vps:
        for p in sorted(nps):
            print(' '.join([get_word(id, sentences)["name"] for id in sorted(nps[p] + [p])]))
