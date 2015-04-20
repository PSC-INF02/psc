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
from abstracter.grammar.systran_parser import parse_systran
from abstracter.grammar.noun_phrases import get_noun_phrases

sents = parse_systran("../systran/3.clean.wsd.linear")
nps = get_noun_phrases(sents)
ref = refactor_nps(nps) # one dict only, by two-tuples indices
resolve_anaphoras_in_place(sents, nps) # add the refersTo tags
print_solution_in_place(sents, nps)
@endcode

Anaphoras can also be resolved without adding the refersTo tags :
@code
sents = systran_parsed_data
nps = get_noun_phrases(sents)
print(nps)
res = resolve_all_anaphoras(sents, nps)
print(res)
truc = refactor_results(nps, res)
print_all_resolution(sents, truc)
@endcode

See the functions documentation.
"""
from abstracter.grammar.utils import *
from abstracter.grammar.noun_phrases import get_noun_phrases, refactor_nps


#####################
# how many previous sentences to check for pronouns
###################

PREV_SENTS = 2


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
        if has_type_in(word, PRONOUN_TAGS):
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
