"""@file anaphora_resolution.py

@brief Resolve anaphoras in a text.

The problem of anaphora resolution is the following : we want
to discover which name or noun phrase a pronoun refers to.

This package uses the Systran parser, but it can be adapted to
other syntax parsing tools, as soon as
the json data provided contains enough information (such as types and tags).

@see util.systran_parser.py

Example :
@code
nps = get_noun_phrases(sents)
ref = refactor_nps(nps) # one dict only, by two-tuples indices
resolve_anaphoras_in_place(sents, nps) # add the refersTo tags
@endcode
"""

##############################
# Types of words in noun phrases (systrans's types)
########################

NOUN_PHRASES_TYPES = ["noun:propernoun", "noun:common", "noun:acronym",
                      "det", "adj", "numeric"]

################################
# Types of proper nouns
############################

PROPERNOUNS = ["noun:propernoun", "noun:acronym"]

##########################
# Types of pronouns
############################

PRONOUN_TAGS = ["pron"]

###################################
# heuristically, only words tagged as objects or agents of verbs
# make good noun phrases
# however, this is not always the case. After running some tests,
# we discovered we had to use also direct objects.
##############################

MASTER_NOUN_TAGS = ["OBJECT_OF_VERB", "AGENT_OF_VERB", "DIROBJ_OF"]

#####################################
# When we get a head noun, we want to
# construct the whole noun phrase :
# with TO_ADD, add directly words with the head noun's tags
# with TO_BE_ADDED, add words from the phrase that
# are linked with the head noun
###################################

TO_ADD = ["MODIFIED_ON_LEFT", "MODIFIED_BY_ADJ"]  # "MODIFIED_ON_RIGHT", ??
TO_BE_ADDED = ["MODIFIES_RIGHT_HEAD", "MODIFIES_ANOTHER_NOUN",
               "SEMANTIC_MODIFIER_OF"]

#######################################
# indefinite articles
##############################

INDEFINITE = ["a"]


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
    """
    Getting tag information.

    @return The result may be "0", "1" or an integer
    (if the tag is a link to another word), or None
    if the tag doesn't appear.
    """
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
    return (get_word(id, sentences)["type"]) in PROPERNOUNS


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

    This allows the user to run some tests.

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
    * {"words": [{...}, {...}, {...}], "text": "...", "id": 6}
    Where each word has the form :
    * {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @param nps Not refactored noun phrases, that is, a list of dictionaries.

    @return A dict of relations between the pronouns of the studied sentence,
    and noun phrases, identified with their head noun.
    Like :
    {(1, 29): (1, 28), (1, 30): (0, 15)}
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

    # list of all nps ids
    all_nps = []
    for d in nps:
        all_nps += d.keys()

    # ids in all_nps are two-tuples : sentence id and word id in the sentence
    # each noun phrase is represented by its head noun
    words = sents[len(sents) - 1]["words"]
    # the words of the studied sentence
    sent_id = sents[len(sents) - 1]["id"]
    # the id of the studied sentence

    # first, recognize pronouns
    for word in words:
        if _has_type_in(word, PRONOUN_TAGS):
            res[(sent_id, word["id"])] = {}

    # then, run some checks
    # for each pronoun
    for pron_id in res:
        # for each noun phrase
        for np_id in all_nps:
            # proximity between noun phrase and pronoun
            # + the noun phrase has to appear before the pronoun
            if (pron_id < np_id):
                res[pron_id][np_id] = -100
            else:
                res[pron_id][np_id] = (np_id[0] - pron_id[0]) * 8
                res[pron_id][np_id] -= (pron_id[1] - np_id[1]) * 0.5

            # plural or singular
            for tag in ["PL", "SG"]:
                temp = get_tag(sents, np_id, tag)
                temp2 = get_tag(sents, pron_id, tag)
                if (temp2 and temp and temp2 == temp):
                    res[pron_id][np_id] += 10
                if (temp2 and temp and not temp2 == temp):
                    res[pron_id][np_id] -= 100

            # human or not human
            temp = get_tag(sents, np_id, "HUMAN")
            temp2 = get_tag(sents, pron_id, "HUMAN")
            # print(get_word(np_id, sents)["name"] + "  " + temp.__str__())
            if (temp and temp2 and temp2 == temp):
                # print(get_word(np_id, sents)["name"] + "  " + get_word(pron_id, sents)["name"])
                res[pron_id][np_id] += 10
            if (temp and temp2 and not temp2 == temp):
                res[pron_id][np_id] -= 30

        # check antecedent data (given by systran)
        #for tag in ANTECEDENT_TAGS:
        #    if get_tag(sents, (sent_id, pron_id), tag) and (sent_id, get_tag(sents, (sent_id, pron_id), tag)) in res[pron_id]:
        #        res[pron_id][(sent_id - len(sents) + 1, _get_tag(words[pron_id], tag))] = 1
    # other checkings
    # 1 : noun phrases that appear at the beginning of a sentence
    # get a better score
    for i in range(len(nps)):
        temp = list(nps[i].keys())
        temp.sort()
        for pron_id in res:
            if temp:
                res[pron_id][temp[0]] += 5

    # 3 : lexical reiteration (with previous sentences also)
    # we check the head nouns
    # each repeted head noun gains 1
    for np_id in all_nps:
        temp = 0
        for np_id2 in all_nps:
            if get_word(np_id, sents)["norm"] == get_word(np_id2, sents)["norm"]:
                temp += 1
        if temp > 1:
            for pron_id in res:
                res[pron_id][np_id] += 5

    # 4 : prepositional or non prepositional NP : "into the VCR"
    # + ranking : subject, direct object, indirect object
    # definite noun phrases also
    for np_id in all_nps:
        # prepositional Noun phrases
        if get_tag(sents, np_id, "MODIFIED_BY_PREP1") is not None:
            for pron_id in res:
                res[pron_id][np_id] -= 2
        if get_tag(sents, np_id, "AGENT_OF_VERB") is not None:
            for pron_id in res:
                res[pron_id][np_id] += 10
        if get_tag(sents, np_id, "OBJECT_OF_VERB") is not None:
            for pron_id in res:
                res[pron_id][np_id] -= 2
        if get_tag(sents, np_id, "DIROBJ_OF") is not None:
            for pron_id in res:
                res[pron_id][np_id] -= 10
        # indefinite (indefinite article)
        if is_indefinite(sents, nps[np_id[0] - offset][np_id]):
            for pron_id in res:
                res[pron_id][np_id] -= 10
        # propernoun
        if is_propernoun(np_id, sents):
            for pron_id in res:
                res[pron_id][np_id] += 10

    # 5 : collocation pattenrn

    # 6 :immediate reference

    # 7 : term preference

    # get the better
    result = {}
    for pron_id in res:
        temp = -1000
        best = 0
        for double_id in res[pron_id]:
            if res[pron_id][double_id] > temp:
                temp = res[pron_id][double_id]
                best = double_id
        result[pron_id] = best
    # print(result)
    return result


def resolve_all_anaphoras(sents, nps):
    """
    Resolve all anaphoras in a text after computing the noun phrases.

    @param nps Noun phrases (list of dicts), already computed (double ids).
    @param sents The sentences (directly parsed from systran).
    @see get_noun_phrases

    @return A list of dicts like :
    * {(1, 29): (1, 28), (1, 30): (0, 15)}
    For each sentence.
    """
    assert len(sents) > 0
    assert len(nps) == len(sents)
    res = []
    for i in range(len(sents)):
        res.append(resolve_anaphoras(sents[max(i - PREV_SENTS, 0): i + 1], nps[max(i - PREV_SENTS, 0):i + 1]))
    return res


def resolve_anaphoras_in_place(sents, nps=None):
    """
    Resolve all anaphoras by adding a tag "refersTo" pointing
    to the specified head noun.

    @warning : The tag "refersTo" gives a two-tuple.
    """
    # in case the noun phrases were'nt computed
    if not nps:
        nps = get_noun_phrases(sents)
    resolve_results = resolve_all_anaphoras(sents, nps)
    for i in range(len(sents)):
        for pron_id in resolve_results[i]:
            # we find the pronoun and modify it
            get_word(pron_id, sents)["tags"]["refersTo"] = resolve_results[i][pron_id]


def print_all_resolution(sents, refactored):
    """
    Check the solution obtained.

    This allows the user to run some tests.
    @param sents Sentences.
    @param refactored Refactored results of resolve_all_anaphoras on sents.
    @see refactor_results
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
    As resolve results are indexed by the head noun,
    this function refactor them in order to print
    them without any nps information.

    @param nps Noun phrases (double ids), as a list of dicts.
    @param resolve_results Result of resolve_all_anaphoras.
    List of dicts also.

    @return A list of dicts like :
    * {(1, 1): [(0, 1), (0, 2)]}
    Where (1, 1) is the pronoun id in the sentences, and
    (0, 1), (0, 2) ids of words forming a noun phrase.
    @see get_noun_phrases
    """
    assert len(nps) == len(resolve_results)
    result = []
    nps2 = refactor_nps(nps)
    for i in range(len(resolve_results)):
        temp = {}
        for id in resolve_results[i]:
            tmp = resolve_results[i][id]
            tmp2 = nps2[tmp]
            temp[id] = sorted(tmp2 + [tmp])
        result.append(temp)
    return result


def print_solution_in_place(sents, nps):
    refactored_nps = refactor_nps(nps)
    for i in range(len(sents)):
        sent = sents[i]
        for word in sent["words"]:
            if not _has_tag_in(word, ["refersTo"]):
                print(word["name"], end=" ")
            else:
                the_head_noun = word["tags"]["refersTo"]
                the_prop = sorted(refactored_nps[the_head_noun] + [the_head_noun])
                the_words = [get_word(full_id, sents)["name"] for full_id in the_prop]
                print(word["name"] + " ( " + ' '.join(the_words) + " ) ", end="")
        print("\n")


def demo(systran_parsed_data):
    sents = systran_parsed_data
    nps = get_noun_phrases(sents)
    print(nps)
    res = resolve_all_anaphoras(sents, nps)
    print(res)
    truc = refactor_results(nps, res)
    print_all_resolution(sents, truc)


def demo2(sents):
    nps = get_noun_phrases(sents)
    print(nps)
    print_noun_phrases(sents)
    resolve_anaphoras_in_place(sents, nps)
    print_solution_in_place(sents, nps)
