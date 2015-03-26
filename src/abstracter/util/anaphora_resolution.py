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


def _get(word, info):
    return word[info]


def _get_tag(word, tag):
    return word["tags"][tag] if tag in word["tags"] else None


def _has_type_in(word, type_list):
    return word["type"] in type_list


#def is_subject(sent, id):
#    return _get_tag(sent, id, "AGENT_OF_VERB") is not None


#def is_object(sent, id):
#    return _get_tag(sent, id, "OBJECT_OF_VERB") is not None


# def is_definite(sent, id_list):
#     """
#     Check if it is a definite noun phrase, i.e
#     if it contains a definite article or
#     a possessive or demonstrative pronoun.
#     """
#     res = False
#     for id in id_list:
#         res = res or sent[id]["norm"] in DEFINITE
#     return res


# def is_prepositional(sent, id):
#     return _get_tag(sent, id, "MODIFIED_BY_PREP1") is not None


def _has_tag_in(word, tag_list):
    res = False
    for tag in tag_list:
        res = res or _get_tag(word, tag)
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


def get_noun_phrases(words):
    """
    This function get noun phrases from a sentence,
    (parsed from crego_to_json).
    The noun phrases are given as a dict.
    Each one is determined by one element.
    @warning Use it on one sentence only. It cannot work with a full text.

    @param sent
    @return Dict.
    """
    res = {}
    # recognize subjects and objects
    for term_id in range(len(words)):
        word = words[term_id]
        if word["type"] in NOUN_PHRASES_TYPES and _has_tag_in(word, MASTER_NOUN_TAGS):
            res[term_id] = []
            # add all related words
            for tag in TO_ADD:
                temp = _get_tag(word, tag)
                if temp:
                    res[term_id].append(temp)
    # ckeck all words in the phrase, in case we have forgotten one
    for term_id in range(len(words)):
        word = words[term_id]
        if term_id not in res and _has_type_in(word, NOUN_PHRASES_TYPES):
            for tag in TO_BE_ADDED:
                temp = _get_tag(word, tag)
                if temp in res:
                    if term_id not in res[temp]:
                        res[temp].append(term_id)
    for term_id in res:
        res[term_id].sort()
    return res


def print_noun_phrases(words, noun_phrases):
    """
    Utilitary to check if we've obtained the proper noun phrases.

    @param words List of words ordered by id.
    """
    for p in sorted(noun_phrases):
        print(' '.join([words[id]["name"] for id in (noun_phrases[p] + [p])]))


def resolve_anaphoras(sents, nps):
    """
    @warning : take in account the way noun phrases in the previous sentences
    are numbered.

    @param sents Sentences list. The last is the principal sentence.
    @param nps List also (of dicts). All nps are already computed.
    @return A dict of relations between the pronouns of the first sentence, and noun phrases,
    identified with their master noun.
    """
    assert len(sents) == len(nps)
    assert len(sents) > 0
    res = {}
    np_keys = []
    for i in range(len(nps)):
        np_keys += [(sents[i]["id"], id) for id in sorted(nps[i])]
    # ids in np_keys : sentence id (relative to the last one) and word id in the sentence
    # each noun phrase is represented by its master noun
    words = sents[len(sents) - 1]["words"]
    sent_id = sents[len(sents) - 1]["id"]
    # recognize pronouns
    for word in words:
        if _has_type_in(word, PRONOUN_TAGS):
            res[word["id"]] = {}
    for term_id in res:
        for full_id in np_keys:
            # proximity between noun phrase and pronoun
            # + the noun phrase has to appear before the pronoun
            if (term_id > full_id[1] or full_id[0] < sent_id):
                res[term_id][full_id] = full_id[1] - term_id - (sent_id - full_id[0])* 5
            else:
                res[term_id][full_id] = -100

            # check gender, etc
            for tag in DISCRIMINATIVE_TAGS:
                #print(full_id[0].__str__()+" "+full_id[1].__str__()+" "+sents[len(sents) - full_id[0] - 1]["words"].__str__()+" ")
                temp = _get_tag(sents[len(sents) - 1 + full_id[0] - sent_id]["words"][full_id[1]], tag)
                if (_get_tag(words[term_id], tag) and temp
                   and not _get_tag(words[term_id], tag) == temp):
                    res[term_id][full_id] -= 100
        # check antecedent data (given by systran)
        for tag in ANTECEDENT_TAGS:
            if _get_tag(words[term_id], tag) and (sent_id - len(sents) + 1, _get_tag(words[term_id], tag)) in res[term_id]:
                res[term_id][(sent_id - len(sents) + 1, _get_tag(words[term_id], tag))] = 1
    # other checkings
    # 1 : noun phrases that appear at the beginning of a sentence
    # get a better score
    for i in range(len(nps)):
        temp = list(nps[i].keys())
        temp.sort()
        for term_id in res:
            res[term_id][i - len(sents) + 1 + sent_id, temp[0]] += 1

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
    # print(result)
    return result


def get_all_noun_phrases(sents):
    return [get_noun_phrases(sent["words"]) for sent in sents]


def resolve_all_anaphoras(sents, nps):
    # nps = [get_noun_phrases(sent["words"]) for sent in sents]
    assert len(sents) > 0
    assert len(nps) == len(sents)
    res = []
    for i in range(len(sents)):
        # print(resolve_anaphoras(sents[max(i - 2, 0): i + 1], nps[max(i - 2, 0):i + 1]))
        res.append(resolve_anaphoras(sents[max(i - 2, 0): i + 1], nps[max(i - 2, 0):i + 1]))
    return res


def print_all_resolution(sents, nps, resolve_results):
    assert len(sents) == len(nps)
    assert len(resolve_results) == len(nps)
    sent_id = sents[0]["id"]
    for j in range(len(sents)):
        words = sents[j]["words"]
        for i in range(len(words)):
            if i not in resolve_results[j]:
                print(words[i]["name"], end=" ")
            else:
                the_sent = resolve_results[j][i][0] - sent_id
                the_master_noun = resolve_results[j][i][1]
                the_prop = nps[the_sent][resolve_results[j][i][1]] + [resolve_results[j][i][1]]
                the_words = [sents[the_sent]["words"][id]["name"] for id in the_prop]
                print(words[i]["name"] + " ( " + ' '.join(the_words) + " ) ", end="")
        print("\n")


def print_resolution(sents, nps, resolve_result):
    for i in range(len(sents) - 1):
        print(sents[i]["text"])
    words = sents[len(sents) - 1]["words"]
    for i in range(len(words)):
        if i not in resolve_result:
            print(words[i]["name"], end=" ")
        else:
            the_sent = len(sents) - 1 - resolve_result[i][0]
            the_master_noun = resolve_result[i][1]
            the_prop = nps[the_sent][resolve_result[i][1]] + [resolve_result[i][1]]
            the_words = [sents[the_sent]["words"][id]["name"] for id in the_prop]
            print(words[i]["name"] + " ( " + ' '.join(the_words) + " ) ", end="")
    print("\n")


def resolve_periphrasis(sent, noun_phrases):
    """

    @return A dict of relations between the noun phrases.
    """
    pass
