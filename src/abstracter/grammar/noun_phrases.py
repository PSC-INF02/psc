"""@file noun_phrases.py
@brief Getting noun phrases in a text (parsed to json).

Example :
@code
from abstracter.grammar.systran_parser import parse_systran
from abstracter.grammar.noun_phrases import get_noun_phrases, print_noun_phrases

sents = parse_systran("../systran/3.clean.wsd.linear")
nps = get_noun_phrases(sents)
print(nps)
print_noun_phrases(sents)
@endcode
"""

from abstracter.grammar.utils import NOUN_PHRASES_TYPES, has_tag_in, has_type_in, MASTER_NOUN_TAGS, get_word, TO_BE_ADDED, TO_ADD


def get_noun_phrases(sentences):
    """
    @brief This function gets noun phrases from sentences.

    For each sentence, the noun phrases are given as a dict.
    Each one is determined by one element : the head noun.

    The noun phrases are computed with the following algorithm :
    first, we get all possible head nouns, by recognizing some tags
    (objects or subjects of verbs, direct objects are good candidates).
    Then, we expand each noun phrase by adding words that are
    related to the head noun (adjectives, articles...).

    @param sentences A list of sentences given by the systran parser
    (function parse_systran).
    Each sentence is a dict like :
    {"id": ..., "Text": ..., "Words": [...]}
    In the words list, each word is a dict like :
    {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @return A list of dicts. Each one corresponds to a sentence and
    has the following form :
    {(0, 0): [], (0, 8): [(0, 6), (0, 7)]}
    Each id is a two-tuple, corresponding to a word
    (sentence id and word id in the sentence).
    Thus, the information of the tuple's first element is redundant
    with the position of the dict in the resulting list.
    This is more practical.
    For this example, we indicate that there are two noun phrases in
    the sentence 0 : one with the head noun of id (0, 0)
    (first word of this sentence), which is alone,
    and a second with the head noun of id (0, 8) (eigth word), which contains
    also id (0, 6) and (0, 7).

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
               and word["type"] in NOUN_PHRASES_TYPES
               and has_tag_in(word, MASTER_NOUN_TAGS)):
                res[term_id] = []
                # add related words
                for tag in TO_ADD:
                    temp = (sent_id, word["tags"].get(tag, None))
                    if (temp and temp != term_id
                       and temp not in res[term_id]
                       and get_word(temp, sentences)
                       and get_word(temp, sentences)["type"] in NOUN_PHRASES_TYPES):
                        res[term_id].append(temp)

        # ckeck all words in the phrase, in case we have forgotten one
        for word in sent["words"]:
            term_id = (sent_id, word["id"])
            if term_id not in res and has_type_in(word, NOUN_PHRASES_TYPES):
                for tag in TO_BE_ADDED:
                    temp = (sent_id, word["tags"].get(tag, None))
                    if temp in res:
                        if temp != term_id and term_id not in res[temp]:
                            res[temp].append(term_id)
        for term_id in res:
            res[term_id].sort()
        res_list.append(res)
    return res_list


def refactor_nps(noun_phrases):
    """
    Small util to transform the noun_phrases list
    into a single dict.

    @see get_noun_phrases
    """
    res_dict = {}
    for d in noun_phrases:
        for k in d:
            res_dict[k] = d[k]
    return res_dict


def print_noun_phrases(sentences):
    """
    Utilitary to check if we've obtained the proper noun phrases.

    This allows the user to run some tests.

    @see get_noun_phrases
    """
    noun_phrases = get_noun_phrases(sentences)
    for nps in noun_phrases:
        for p in sorted(nps):
            print(' '.join([get_word(id, sentences)["name"] for id in (nps[p] + [p])]))
