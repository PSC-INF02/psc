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

MASTER_NOUN_TAGS = ["OBJECT_OF_VERB", "AGENT_OF_VERB", "DIROBJ_OF"]# added dirobj_of

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

#######################################


def get_word(id, sents):
    """
    Utilitary : getting a word in a list of sentences.

    @param sents List of sentences given by the systran parser.
    @param id Two-tuple : id[0] is the sentence id,
    id[1] is the word id in the sentence
    @return A word (dictionary of attributes).
    """
    for sent in sents:
        if sent["id"] == id[0]:
            for word in sent["words"]:
                if word["id"] == id[1]:
                    return word
    return None


def _get_tag(word, tag):
    return word["tags"][tag] if tag in word["tags"] else None


def _has_type_in(word, type_list):
    return word["type"] in type_list


def is_indefinite(sentences, id_list):
    """
    Check if it is a definite noun phrase, i.e
    if it contains a definite article or
    a possessive or demonstrative pronoun.
    """
    for id in id_list:
        if get_word(id, sentences)["norm"] in INDEFINITE:
            return True
    return False


def is_propernoun(id, sentences):
    return (get_word(id, sentences)["type"]) in ["noun:propernoun", "noun:acronym"]


def _has_tag_in(word, tag_list):
    for tag in tag_list:
        if _get_tag(word, tag):
            return True
    return False


def get_tag(sents, full_id, tag):
    tmp = get_word(full_id, sents)
    return tmp["tags"][tag] if tag in tmp["tags"] else None


def get_noun_phrases(sentences):
    """
    @brief This function get noun phrases from sentences.

    For each sentence, the noun phrases are given as a dict.
    Each one is determined by one element : the master noun.

    The noun phrases are computed with the following algorithm :
    first, we get all possible master nouns, by recognizing some tags
    (objects or subjects of verbs, direct objects are good candidates).
    Then, we expand each noun phrase by adding words that are
    related to the master noun (adjectives, articles...).

    @param sentences A list of sentences given by the systran parser
    (function parse_systran).
    Each sentence is a dict like :
    > {"id": ..., "Text": ..., "Words": [...]}
    In the words list, each word is a dict like :
    > {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @see abstracter.util.systran_parser.py
    @return A list of dicts. Each one corresponds to a sentence and
    has the following form :
    > {(0, 0): [], (0, 8): [(0, 6), (0, 7)]}
    Each id is a two-tuple, corresponding to a word (sentence id and word id in the sentence).
    Thus, the information of the tuple's first element is redundant
    with the position of the dict in the resulting list. This is more practical.

    For this example, we indicate that there are two noun phrases in
    the sentence 0 : one with the master noun of id (0, 0)
    (first word of this sentence), which is alone,
    and a second with the master noun of id (0, 8) (eigth word), which contains
    also id (0, 6) and (0, 7).
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
               and _has_tag_in(word, MASTER_NOUN_TAGS)):
                res[term_id] = []
                # add related words
                for tag in TO_ADD:
                    temp = (sent_id, _get_tag(word, tag))
                    if (temp and temp != term_id
                       and temp not in res[term_id]
                       and get_word(temp, sentences)
                       and get_word(temp, sentences)["type"] in NOUN_PHRASES_TYPES):
                        res[term_id].append(temp)

        # ckeck all words in the phrase, in case we have forgotten one
        for word in sent["words"]:
            term_id = (sent_id, word["id"])
            if term_id not in res and _has_type_in(word, NOUN_PHRASES_TYPES):
                for tag in TO_BE_ADDED:
                    temp = (sent_id, _get_tag(word, tag))
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

    @see get_noun_phrases
    """
    noun_phrases = get_noun_phrases(sentences)
    for nps in noun_phrases:
        for p in sorted(nps):
            print(' '.join([get_word(id, sentences)["name"] for id in (nps[p] + [p])]))


def resolve_anaphoras(sents, nps):
    """
    Resolve anaphoras, meaning, find a noun phrase corresponding
    to each pronoun.
    The algorithm used is detailed in the report. It uses several ideas
    to compute a score,
    then ranks, for each pronoun, the candidates.

    @see abstracter.util.parse_systran
    @param sents Sentences list. The last is the principal sentence
    (the one studied). All noun phrases in these sentences are
    possible candidates.
    Each sentence is a dict, resulting from parse_systran, of the form :
    > {"words": [{...}, {...}, {...}], "text": "...", "id": 6}
    Where each word has the form :
    > {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @return A dict of relations between the pronouns of the studied sentence,
    and noun phrases, identified with their master noun.
    Like :
    > {(1, 29): (1, 28), (1, 30): (0, 15)}
    Which means the pronoun of id 29 in the last sentence (sentence 1)
    can be linked with
    the noun phrase identified by 28 in the sentence of id 1
    (thus the same sentence).
    And the pronoun of id 30 in the last sentence can be linked with
    the noun phrase identified by 15 in the sentence of id 0.
    """
    assert len(sents) == len(nps)
    assert len(sents) > 0
    assert 1 + sents[len(sents) - 1]["id"] - len(sents) == sents[0]["id"]
    # ie : all sentences are there
    offset = sents[0]["id"]
    # id of the first sentence
    res = {}

    np_keys = []
    for d in nps:
        np_keys += d.keys()
    # ids in np_keys : sentence id and word id in the sentence
    # each noun phrase is represented by its master noun
    words = sents[len(sents) - 1]["words"]
    sent_id = sents[len(sents) - 1]["id"]# the id of the studied sentence

    # first, recognize pronouns
    for word in words:
        if _has_type_in(word, PRONOUN_TAGS):
            res[(sent_id, word["id"])] = {}

    # then, run some checks
    # for each pronoun
    for term_id in res:
        # for each noun phrase
        for full_id in np_keys:
            # proximity between noun phrase and pronoun
            # + the noun phrase has to appear before the pronoun
            #if (term_id > full_id[1] or full_id[0] < sent_id):
            if (term_id[1] > full_id[1] or full_id[0] < term_id[0]):
                res[term_id][full_id] = full_id[1] - \
                    term_id[1] - (term_id[0] - full_id[0]) * 7
            else:
                res[term_id][full_id] = -100

            for tag in ["PL", "SG"]:
                temp = get_tag(sents, full_id, tag)
                if (get_tag(sents, term_id, tag) and temp
                   and not get_tag(sents, term_id, tag) == temp):
                    res[term_id][full_id] -= 4
            temp = get_tag(sents, full_id, "HUMAN")
            temp2 = get_tag(sents, term_id, "HUMAN")
            # print(get_word(full_id, sents)["name"] + "  " + temp.__str__())
            if (temp and temp2
               and temp2 == temp):
                # print(get_word(full_id, sents)["name"] + "  " + get_word(term_id, sents)["name"])
                res[term_id][full_id] += 100

        # check antecedent data (given by systran)
        #for tag in ANTECEDENT_TAGS:
        #    if get_tag(sents, (sent_id, term_id), tag) and (sent_id, get_tag(sents, (sent_id, term_id), tag)) in res[term_id]:
        #        res[term_id][(sent_id - len(sents) + 1, _get_tag(words[term_id], tag))] = 1
    # other checkings
    # 1 : noun phrases that appear at the beginning of a sentence
    # get a better score
    for i in range(len(nps)):
        temp = list(nps[i].keys())
        temp.sort()
        for term_id in res:
            if temp:
                res[term_id][temp[0]] += 5

    # 3 : lexical reiteration (with previous sentences also)
    # we check the head nouns
    # each repeted head noun gains 1
    # we could include here synonymy data
    #for id in np_keys:
    #    temp = 0
    #    for id2 in np_keys:
    #        if sents[id2[0] - offset]["words"][id2[1]]["norm"] == sents[id[0] - offset]["words"][id[1]]["norm"]:
    #            temp += 1
    #    if temp > 1:
    #        for term_id in res:
    #            res[term_id][id] += 1

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
        if is_indefinite(sents, nps[full_id[0] - offset][full_id]):
            for term_id in res:
                res[term_id][full_id] -= 4
        if is_propernoun(full_id, sents):
            for term_id in res:
                res[term_id][full_id] += 100

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

    @param nps Noun phrases (list of dicts), already computed.
    @see get_noun_phrases
    @param sents The sentences (directly parsed from systran).
    """
    assert len(sents) > 0
    assert len(nps) == len(sents)
    res = []
    for i in range(len(sents)):
        res.append(resolve_anaphoras(sents[max(i - PREV_SENTS, 0): i + 1], nps[max(i - PREV_SENTS, 0):i + 1]))
    return res


def print_all_resolution(sents, refactored):
    """
    Check the solution obtained.
    """
    assert len(sents) == len(refactored)
    sent_id = sents[0]["id"]
    for sent in sents:
        for word in sent["words"]:
            if (sent["id"], word["id"]) not in refactored[sent["id"]]:
                print(word["name"], end=" ")
            else:
                the_prop = refactored[sent["id"]][(sent["id"], word["id"])]
                the_words = [get_word(full_id, sents)["name"] for full_id in the_prop]
                print(word["name"] + " ( " + ' '.join(the_words) + " ) ", end="")
        print("\n")


def refactor_results(nps, resolve_results):
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
    nps2 = refactor_nps(nps)
    for i in range(len(resolve_results)):
        temp = {}
        for id in resolve_results[i]:
            tmp = resolve_results[i][id]
            tmp2 = nps2[tmp]
            temp[id] = sorted(tmp2 + [tmp]) # [(tmp[0], j) for j in sorted(tmp2 + [tmp[1]])]
        result.append(temp)
    return result


def demo(systran_parsed_data):
    sents = systran_parsed_data
    nps = get_noun_phrases(sents)
    print(nps)
    res = resolve_all_anaphoras(sents, nps)
    print(res)
    truc = refactor_results(nps, res)
    print_all_resolution(sents, truc)
