"""@file anaphor_resolution.py

Resolve anaphors.
"""

NOUN_PHRASES_TYPES = ["noun:propernoun", "noun:common", "noun:acronym",
                      "det", "adj", "numeric"]
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

TO_ADD = ["MODIFIED_ON_LEFT", "MODIFIED_BY_ADJ"]# "MODIFIED_ON_RIGHT", ??
TO_BE_ADDED = ["MODIFIES_RIGHT_HEAD", "MODIFIES_ANOTHER_NOUN",
               "SEMANTIC_MODIFIER_OF"]

#######################################
# indefinite articles
##############################

INDEFINITE = ["a"]


DISCRIMINATIVE_TAGS = ["PL", "SG"]
ANTECEDENT_TAGS = ["ANTECEDENT"]


#####################
# how many previous sentences to check
###################

PREV_SENTS = 2


def _get_tag(word, tag):
    return word["tags"][tag] if tag in word["tags"] else None


def _has_type_in(word, type_list):
    return word["type"] in type_list


def is_subject(word):
    return _get_tag(word, "AGENT_OF_VERB") is not None


def is_object(word):
    return _get_tag(word, "OBJECT_OF_VERB") is not None


def is_indefinite(words, id_list):
    """
    Check if it is a definite noun phrase, i.e
    if it contains a definite article or
    a possessive or demonstrative pronoun.
    """
    res = False
    for id in id_list:
        res = res or words[id]["norm"] in INDEFINITE
    return res


def is_propernoun(words, id_list):
    res = False
    for id in id_list:
        res = res or words[id]["type"] in ["noun:propernoun", "noun:acronym"]
    return res


def _has_tag_in(word, tag_list):
    res = False
    for tag in tag_list:
        res = res or _get_tag(word, tag)
    return res


def get_noun_phrases(words):
    """
    This function get noun phrases from a sentence,
    (parsed from crego_to_json).
    The noun phrases are given as a dict.
    Each one is determined by one element : the master noun.

    @param words A list of words given by the systran parser :
    each word is a dict like :
    >> {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}
    @return A dict like :
    >> {0: [], 8: [6, 7]}
    Indicating that there are two noun phrases ;
    one with the master noun of id 0 (first word), which is alone,
    and a second with the master noun of id 8 (eigth word), which contains
    also id 6 and 7.
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
                if temp and words[temp]["type"] in NOUN_PHRASES_TYPES:
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


def get_all_noun_phrases(sents):
    return [get_noun_phrases(sent["words"]) for sent in sents]


def print_noun_phrases(words, noun_phrases):
    """
    Utilitary to check if we've obtained the proper noun phrases.

    @param words List of words ordered by id.
    @param noun_phrases Result of get_noun_phrases.
    """
    for p in sorted(noun_phrases):
        print(' '.join([words[id]["name"] for id in (noun_phrases[p] + [p])]))


# way to make this function inline ?
def get_tag(sents, full_id, tag):
    tmp = sents[len(sents) - 1 + full_id[0] - sents[len(sents) - 1]["id"]]["words"][full_id[1]]
    return tmp["tags"][tag] if tag in tmp["tags"] else None


def get_word(sents, full_id):
    return sents[len(sents) - 1 + full_id[0] - sents[len(sents) - 1]["id"]]["words"][full_id[1]]


# id ?
def id_change(sents, id):
    return len(sents) - 1 + id - sents[len(sents) - 1]["id"]


def resolve_anaphoras(sents, nps):
    """
    Resolve anaphoras, meaning, find a noun phrase corresponding
    to each pronoun.
    The algorithm used is detailed in the report. It uses several ideas
    to compute a score,
    then ranks, for each pronoun, the candidates.

    @see abstracter.util.parse_systran
    @param sents Sentences list. The last is the principal sentence
    (the one studied).
    Each sentence is a dict, resulting from parse_systran, of the form :
    >> {"words": [{...}, {...}, {...}], "text": "...", "id": 6}
    Where each word has the form :
    >> {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @param nps List of dicts of get_noun_phrases results.
    All nps are already computed.
    Each np dict corresponds to a sentence.
    @return A dict of relations between the pronouns of the studied sentence,
    and noun phrases, identified with their master noun.
    Like :
    >> {29: (1, 28), 30: (0, 15)}
    Which means the pronoun of id 29 in the last sentence can be linked with
    the noun phrase identified by 28 in the sentence of id 1.
    And the pronoun of id 155 in the last sentence can be linked with
    the noun phrase identified by 15 in the sentence of id 0.
    """
    assert len(sents) == len(nps)
    assert len(sents) > 0
    assert 1 + sents[len(sents) - 1]["id"] - len(sents) == sents[0]["id"]
    offset = sents[0]["id"]
    # id of the first sentence
    res = {}
    # we recompute the keys of the noun phrases
    np_keys = []
    for i in range(len(nps)):
        np_keys += [(sents[i]["id"], id) for id in sorted(nps[i])]
    # ids in np_keys : sentence id and word id in the sentence
    # each noun phrase is represented by its master noun
    words = sents[len(sents) - 1]["words"]
    sent_id = sents[len(sents) - 1]["id"]

    # first, recognize pronouns
    for word in words:
        if _has_type_in(word, PRONOUN_TAGS):
            res[word["id"]] = {}

    # then, run some checks
    # for each pronoun
    for term_id in res:
        # for each noun phrase
        for full_id in np_keys:
            # proximity between noun phrase and pronoun
            # + the noun phrase has to appear before the pronoun
            if (term_id > full_id[1] or full_id[0] < sent_id):
                res[term_id][full_id] = full_id[1] - \
                    term_id - (sent_id - full_id[0]) * 7
            else:
                res[term_id][full_id] = -100

            for tag in ["PL", "SG"]:
                temp = get_tag(sents, full_id, tag)
                if (_get_tag(words[term_id], tag) and temp
                   and not _get_tag(words[term_id], tag) == temp):
                    res[term_id][full_id] -= 4
            temp = get_tag(sents, full_id, "HUMAN")
            if (_get_tag(words[term_id], "HUMAN") and get_tag(sents, full_id, "HUMAN")
               and _get_tag(words[term_id], "HUMAN") == temp):
                res[term_id][full_id] += 10

        # check antecedent data (given by systran)
        for tag in ANTECEDENT_TAGS:
            if _get_tag(words[term_id], tag) and (offset, _get_tag(words[term_id], tag)) in res[term_id]:
                res[term_id][(sent_id - len(sents) + 1, _get_tag(words[term_id], tag))] = 1
    # other checkings
    # 1 : noun phrases that appear at the beginning of a sentence
    # get a better score
    for i in range(len(nps)):
        temp = list(nps[i].keys())
        temp.sort()
        for term_id in res:
            res[term_id][i + offset, temp[0]] += 5

    # 3 : lexical reiteration (with previous sentences also)
    # we check the head nouns
    # each repeted head noun gains 1
    # we could include here synonymy data
    for id in np_keys:
        temp = 0
        for id2 in np_keys:
            if sents[id2[0] - offset]["words"][id2[1]]["norm"] == sents[id[0] - offset]["words"][id[1]]["norm"]:
                temp += 1
        if temp > 1:
            for term_id in res:
                res[term_id][id] += 1

    # 4 : prepositional or non prepositional NP : "into the VCR"
    # + ranking : subject, direct object, indirect object
    # definite noun phrases also
    for full_id in np_keys:
        # prepositional Noun phrases
        if get_tag(sents, full_id, "MODIFIED_BY_PREP1") is not None:
            for term_id in res:
                res[term_id][full_id] -= 2
        if get_tag(sents, full_id, "AGENT_OF_VERB") is not None:
            for term_id in res:
                res[term_id][full_id] += 2
        if get_tag(sents, full_id, "OBJECT_OF_VERB") is not None:
            for term_id in res:
                res[term_id][full_id] -= 2
        if is_indefinite(sents[id_change(sents, full_id[0])]["words"], nps[full_id[0] - offset][full_id[1]]):
            for term_id in res:
                res[term_id][full_id] -= 4
        if is_propernoun(sents[id_change(sents, full_id[0])]["words"], nps[full_id[0] - offset][full_id[1]]):
            for term_id in res:
                res[term_id][full_id] += 4

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


def resolve_all_anaphoras(sents, nps):
    """
    Resolve all anaphoras in a text after computing the noun phrases.

    @param nps Noun phrases (list), already computed.
    @param sents The sentences.
    """
    assert len(sents) > 0
    assert len(nps) == len(sents)
    res = []
    for i in range(len(sents)):
        res.append(resolve_anaphoras(sents[max(i - PREV_SENTS, 0): i + 1], nps[max(i - PREV_SENTS, 0):i + 1]))
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


def refactor_results(offset, nps, resolve_results):
    """
    As resolve results are indexed by the master noun,
    this function refactor them in order to print
    them without any nps information.

    @param nps Noun phrases {0: [], 8: [6, 7]}
    @param resolve_results {29: (1, 28), 30: (0, 15)}

    @return A list of dicts like :
    > {1: [(0, 1), (0, 2)]}
    Where is the pronoun id in the sentence, and
    (0, 1), (0, 2) ids of words forming a noun phrase.
    """
    assert len(nps) == len(resolve_results)
    result = []
    for i in range(len(resolve_results)):
        temp = {}
        for id in resolve_results[i]:
            tmp = resolve_results[i][id]
            tmp2 = nps[tmp[0] - offset][tmp[1]]
            temp[id] = [(tmp[0], j) for j in sorted(tmp2 + [tmp[1]])]
        result.append(temp)
    return result


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


def demo(systran_parsed_data):
    sents = systran_parsed_data
    nps = get_all_noun_phrases(sents)
    print(nps)
    res = resolve_all_anaphoras(sents, nps)
    print(res)
    truc = refactor_results(sents[0]["id"], nps, res)
    for t in truc:
        print(t)
    print_all_resolution(sents, nps, res)
