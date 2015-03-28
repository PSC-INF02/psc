"""
@file names_resolution.py
@brief Resolve names in systran parsed data,
may also add some information to it.
"""

from abstracter.concepts_network import *
from abstracter.util.distance import levenshtein


DEFAULT_CN = "rc"
NAMES_TYPES = ["noun:propernoun"]
# don't take acronyms for refactoring


def _refactor(names_dict):
    for name in names_dict:
        names_dict[name] = names_dict[name].lower().replace('_+_', '_').replace(' ', '_')


def refactor_word(word):
    return word.lower().replace('_+_', '_').replace(' ', '_')


def reduce_names(sentences, cn=None, use_cn=False):
    """
    In order to recognize composed names, using the concepts network.
    We can recognize proper nouns in systran's data.
    This is an on-the-fly reduction ; we modify the data.
    """
    concepts_network = None
    if cn and use_cn:
        concepts_network = cn
    elif use_cn:
        concepts_network = ConceptNetwork()
        print("Loading...")
        concepts_network.load(DEFAULT_CN)
        print("Loading complete !")

    for sentence in sentences:
        temp = ""
        words = sentence["words"].copy()
        skip = 0
        skip2 = 0
        for w_id in range(len(words)):
            w = words[w_id]
            if w["type"] in NAMES_TYPES:
                skip += 1
                if temp:
                    temp = temp + "_+_" + w["name"]
                else:
                    temp = w["name"]
                if use_cn:
                    if concepts_network.has_node(refactor_word(temp + "_+_" + w["name"])):
                        sentence["words"][w_id]["name"] = temp + "_+_" + w["name"]
                        del sentence["words"][w_id + 1: w_id + 1 + skip]
                    # sentence["words"] = sentence["words"][0:w_id] + sentence["words"][w_id + skip:len(sentence["words"])]
            elif temp:
                if not use_cn:
                    sentence["words"][w_id - skip2 - skip]["name"] = temp
                    # print("deleted : " + (w_id - skip - skip2 + 1).__str__() + " to "+ (w_id - skip2).__str__())
                    del sentence["words"][w_id - skip - skip2 + 1: w_id - skip2]
                skip2 += skip - 1
                skip = 0
                temp = ""
        offset = sentence["words"][0]["id"]
        for w_id in range(len(sentence["words"])):
            sentence["words"][w_id]["id"] = w_id + offset
#    return sentences


def match_entities(sentences, cn=None, activate=False):
    """
    Names or subjects that appear in a sentence are linked together and
    to entities in the conceptsNetwork.

    @param cn conceptsNetwork
    @param sentence A sentence, parsed with the systran parser.
    > {"words": [{...}, {...}, {...}], "text": "...", "id": 6}
    Where each word has the form :
    > {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @return A dict of id : entity in the ConceptNetwork (or name
    itself if this entity doesn't exist). Id is a double id, that is,
    sentence id and word id in the sentence.
    """
    concepts_network = None
    if cn:
        concepts_network = cn
    else:
        concepts_network = ConceptNetwork()
        print("Loading...")
        concepts_network.load(DEFAULT_CN)
        print("Loading complete !")

    names_dict = {}
    for sentence in sentences:
        for w in sentence["words"]:
            if w["type"] in NAMES_TYPES:
                names_dict[(sentence["id"], w["id"])] = w["name"]

    # first : refactor the names in names_dict (replace spaces with underscores...)
    _refactor(names_dict)

    # match in the cn
    matched = list()
    to_match = sorted(list(names_dict.keys()))
    for id in names_dict:
        if concepts_network.has_node(names_dict[id]):
            to_match.remove(id)
            matched.append(id)
    matched.sort()
    to_match.sort()
    
    # match names together
    to_match2 = to_match.copy()
    matched2 = matched.copy()
    for i in to_match2:
        for j in matched2:
            if names_dict[i] in names_dict[j] and j < i:# and j < i
                names_dict[i] = names_dict[j]
                if i not in matched:
                    matched.append(i)
                    to_match.remove(i)
    matched.sort()
    to_match.sort()
    # print([names_dict[i] for i in to_match])
    # print([names_dict[i] for i in matched])

    # activate and search for complementary names... (does'nt work yet)
    if activate:
        possible_matches=list(_activate_entities(context,sorted(list(set([names_dict[i] for i in matched])))))
        for id in to_match:
            n, d = _minimize_distance(names_dict[id], possible_matches)
            if d < 0.5:
                names_dict[id] = n
    return names_dict


def print_entities_matching(sentences):
    entities = match_entities(sentences)
    for s in sentences:
        for w in s["words"]:#i in range(len(s["words"])):
            i = (s["id"], w["id"])
            if i not in entities:
                print(s["words"][i[1]]["name"], end=" ")
            else:
                print(s["words"][i[1]]["name"] + " ( " + entities[i] + " ) ", end="")
        print("\n")


def _minimize_distance(name,name_list):
    result=name,-1
    for name2 in name_list:
        d=levenshtein(name,name2, normalized=True, max_dist=-1)
        if result[1]<0:
            result=name2,d
        if d<result[1]:
            result=name2,d
    return result


def _activate_entities(context,entities_list):
    for e in entities_list:
        context.activate(e,50)
    context.run(len(entities_list)*5)
    return context.get_activated_nodes()
    #print(list(context.get_activated_nodes()))