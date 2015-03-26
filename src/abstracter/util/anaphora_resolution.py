"""@file anaphor_resolution.py

Resolve anaphors.
"""

NOUN_PHRASES_TYPES = ["noun:propernoun", "noun:common", "noun:acronym", "det", "adj", "numeric"]
PRONOUN_TAGS = ["pron"]

###################################
# heuristically, only words tagged as objects or agents of verbs
# make good noun phrases
# however, this is not always the case -> have to run some tests
##############################

MASTER_NOUN_TAGS = ["OBJECT_OF_VERB", "AGENT_OF_VERB"]

#####################################
# When we get a master noun, we want to
# construct the whole noun phrase :
# with TO_ADD, add directly words with the master noun's tags
# with TO_BE_ADDED, add words from the phrase that
# are linked with the master noun
###################################

TO_ADD = ["MODIFIED_ON_LEFT", "MODIFIED_ON_RIGHT", "MODIFIED_BY_ADJ"]
TO_BE_ADDED = ["MODIFIES_RIGHT_HEAD", "MODIFIES_ANOTHER_NOUN", "SEMANTIC_MODIFIER_OF"]


DEFINITE = ["THE", "HIS", "HER", "THIS", "THESE"]
INDEFINITE = ["A"]

DISCRIMINATIVE_TAGS = ["PL", "SG", "HUMAN"]
ANTECEDENT_TAGS = ["ANTECEDENT"]


def _get_norm(sent, id):
    return sent[id]["norm"]


def _get_tag(sent, id, tag):
    return sent[id]["tags"][tag] if tag in sent[id]["tags"] else None


def _has_type_in(sent, id, type_list):
    return sent[id]["type"] in type_list


def is_subject(sent, id):
    return _get_tag(sent, id, "AGENT_OF_VERB") is not None


def is_object(sent, id):
    return _get_tag(sent, id, "OBJECT_OF_VERB") is not None


def is_definite(sent, id_list):
    """
    Check if it is a definite noun phrase, i.e
    if it contains a definite article or
    a possessive or demonstrative pronoun.
    """
    res = False
    for id in id_list:
        res = res or sent[id]["norm"] in DEFINITE
    return res


def is_prepositional(sent, id):
    return _get_tag(sent, id, "MODIFIED_BY_PREP1") is not None


def _has_tag_in(sent, id, tag_list):
    res = False
    for tag in tag_list:
        res = res or _get_tag(sent, id, tag)
    return res


#################################
# No more dependency with the data structure
#
##############################

def sentence_to_dict(sent):
    """
    Transforms a list into a dict.
    """
    res = dict()
    for i in sent:
        res[i["id"]] = i
    return res


def get_noun_phrases(sent):
    """
    This function get noun phrases from a sentence,
    (parsed from crego_to_json), as a list.
    The noun phrases are given as a dict.
    Each one is determined by one element.
    @warning Use it on one sentence only. It cannot work with a full text.

    @param sent Dict of words by id.
    @return Dict.
    """
    res = {}
    # recognize subjects and objects
    for term_id in sent:
        if _has_type_in(sent, term_id, NOUN_PHRASES_TYPES) and _has_tag_in(sent, term_id, MASTER_NOUN_TAGS):
            res[term_id] = []
            # add all related words
            for tag in TO_ADD:
                temp = _get_tag(sent, term_id, tag)
                if temp:
                    res[term_id].append(temp)
    # ckeck all words in the phrase, in case we have forgotten one
    for term_id in sent:
        if term_id not in res and _has_type_in(sent, term_id, NOUN_PHRASES_TYPES):
            for tag in TO_BE_ADDED:
                temp = _get_tag(sent, term_id, tag)
                if temp in res:
                    if term_id not in res[temp]:
                        res[temp].append(term_id)
    for full_id in res:
        res[full_id].sort()
    return res


def print_noun_phrases(sent, noun_phrases):
    """
    Utilitary to check if we've obtained the proper noun phrases.

    @param sent Dict of words by id.
    """
    for p in sorted(noun_phrases):
        print(' '.join([sent[id]["name"] for id in (noun_phrases[p] + [p])]))


def resolve_anaphoras(sents, nps):
    """
    @warning : take in account the way noun phrases in the previous sentences
    are numbered.

    @param sents List. The first is the principal sentence.
    @param nps List also. All nps are already computed.
    @return A dict of relations between the pronouns of the first sentence, and noun phrases,
    identified with their master noun.
    """
    res = {}
    np_keys = []
    for i in range(len(nps)):
        np_keys += [(i, id) for id in sorted(nps[i])]

    sent = sents[0]["words"]
    # recognize pronouns
    for term_id in sent:
        if _has_type_in(sent, term_id, PRONOUN_TAGS):
            res[term_id] = {}

    for term_id in res:
        for double_id in np_keys:
            # proximity between noun phrase and pronoun
            # + the noun phrase has to appear before the pronoun
            res[term_id][double_id] = double_id[1] - term_id - double_id[0]*10 if (term_id > double_id[1] or double_id[0] > 0) else -100

            # add here : taking into account previous phrases

            # check gender, etc
            for tag in DISCRIMINATIVE_TAGS:
                if (_get_tag(sent, term_id, tag) and _get_tag(sents[double_id[0]]["words"], double_id[1], tag)
                   and not _get_tag(sent, term_id, tag) == _get_tag(sents[double_id[0]]["words"], double_id[1], tag) ):
                    res[term_id][double_id] -= 100
        # check antecedent data (given by systran)
        if _has_tag_in(sent, term_id, ANTECEDENT_TAGS):
            for tag in ANTECEDENT_TAGS:
                if _get_tag(sent, term_id, tag):
                    res[term_id][(0, _get_tag(sent, term_id, tag))] = 1
    # other checkings
    # 1 : noun phrases that appear at the beginning of a sentence
    # get a better score
    # temp = i for i in sorted(nps)
    # for term_id in res:
    #    for i in range(len(nps)):
    #        res[term_id][i, temp[0]] += 1
    # 2 : indicating verbs ?

    # 3 : lexical reiteration (with previous sentences also)
    # we check the head nouns
    # each repeted head noun gains 1
    # we can include here synonymy data
    # for id in np_keys:
    #     temp = 0
    #     for id2 in np_keys:
    #         if _get_norm(sent, id) == _get_norm(sent, id2):
    #             temp += 1
    #     if temp > 1:
    #         for term_id in res:
    #             res[term_id][id] += 1

    # # 4 : prepositional or non prepositional NP : "into the VCR"
    # # + ranking : subject, direct object, indirect object
    # # definite noun phrases also
    # for id in np_keys:
    #     if is_prepositional(sent, id):
    #         for term_id in res:
    #             res[term_id][id] -= 1
    #     if is_object(sent, id):
    #         for term_id in res:
    #             res[term_id][id] -= 1
    #     if is_definite(sent, id):
    #         for term_id in res:
    #             res[term_id][id] += 1            

    # 5 : collocation pattenrn

    # 6 :immediate reference

    # 7 : term preference

    # get the better
    result = {}
    for term_id in res:
        temp = -1000
        best = 0
        for double_id in res[term_id]:
            if res[term_id][double_id] > temp:
                temp = res[term_id][double_id]
                best = double_id
        result[term_id] = best
    print(result)


def resolve_anaphoras1(sent0, np, previous_np1=None, previous_sent1=None, previous_np2=None, previous_sent2=None):
    """
    @warning : take in account the way noun phrases in the previous sentences
    are numbered.

    @param np Noun phrases (dict).
    @param sent0 Raw dict of a sentence (with its id, words, text).
    @return A dict of relations between the pronouns and noun phrases,
    identified with their master noun.
    """
    sent = sent0["words"]
    res = {}
    np_keys = [(sent0["id"], key) for key in sorted(np)]
    if previous_sent1 and previous_np1:
        np_keys = np_keys + [(previous_sent1["id"], key) for key in sorted(previous_np1)]
    if previous_sent2 and previous_np2:
        np_keys = np_keys + [(previous_sent2["id"], key) for key in sorted(previous_np2)]
    print(np_keys)
    # recognize pronouns
    for term_id in sent:
        if _has_type_in(sent, term_id, PRONOUN_TAGS):
            res[term_id] = {}
    for term_id in res:
        for term_id2 in np:
            # proximity between noun phrase and pronoun
            # + the noun phrase has to appear before the pronoun
            res[term_id][term_id2] = term_id2 - term_id if term_id > term_id2 else -100

            # add here : taking into account previous phrases

            # check gender, etc
            for tag in DISCRIMINATIVE_TAGS:
                if (_get_tag(sent, term_id, tag) and _get_tag(sent, term_id2, tag)
                   and not _get_tag(sent, term_id, tag) == _get_tag(sent, term_id2, tag)):
                    res[term_id][term_id2] -= 100
        # check antecedent data (given by systran)
        if _has_tag_in(sent, term_id, ANTECEDENT_TAGS):
            for tag in ANTECEDENT_TAGS:
                if _get_tag(sent, term_id, tag):
                    res[term_id][_get_tag(sent, term_id, tag)] = 1
    # other checkings
    # 1 : noun phrases that appear at the beginning of a sentence
    # get a better score
    first = np_keys[0]
    for term_id in res:
        res[term_id][first] += 1
    # 2 : indicating verbs ?

    # 3 : lexical reiteration (with previous sentences also)
    # we check the head nouns
    # each repeted head noun gains 1
    # we can include here synonymy data
    for id in np_keys:
        temp = 0
        for id2 in np_keys:
            if _get_norm(sent, id) == _get_norm(sent, id2):
                temp += 1
        if temp > 1:
            for term_id in res:
                res[term_id][id] += 1

    # 4 : prepositional or non prepositional NP : "into the VCR"
    # + ranking : subject, direct object, indirect object
    # definite noun phrases also
    for id in np_keys:
        if is_prepositional(sent, id):
            for term_id in res:
                res[term_id][id] -= 1
        if is_object(sent, id):
            for term_id in res:
                res[term_id][id] -= 1
        if is_definite(sent, id):
            for term_id in res:
                res[term_id][id] += 1            

    # 5 : collocation pattenrn

    # 6 :immediate reference

    # 7 : term preference

    # get the better
    result = {}
    for term_id in res:
        temp = -1000
        best = 0
        for term_id2 in res[term_id]:
            if res[term_id][term_id2] > temp:
                temp = res[term_id][term_id2]
                best = term_id2
        result[term_id] = best
    print(result)


def print_resolution(sent, np, resolve_result):
    for i in sorted(sent):
        print(sent[i])


def resolve_periphrasis(sent, noun_phrases):
    """

    @return A dict of relations between the noun phrases.
    """
    pass
