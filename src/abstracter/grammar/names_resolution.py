"""
@file names_resolution.py
@brief Resolve names in systran parsed data,
may also add some information to it.

Example :
@code
from abstracter.grammar.systran_parser import parse_systran

data = parse_systran("../systran/3.clean.wsd.linear")
reduce_names(data)
match_and_replace(data)
@endcode
"""

from abstracter.concepts_network import *
from abstracter.util.distance import levenshtein
from abstracter.grammar.utils import get_word

####################################
# Default loading of the concepts network.
###################################

DEFAULT_CN = "rc3"


#####################################
# Types of the words implied in reducing names.
# we don't take acronyms.
#####################################

NAMES_TYPES = ["noun:propernoun"]


##################################
# Concepts which indicate that
# some entity is a human being.
##################################

HUMAN = ["person"]


def is_human(word, cn):
    """
    Determine if an entity is a human being.

    This adds new information from the ConceptNetwork, into
    the systran data.
    """
    for h in HUMAN:
        if cn.has_edge(word, h):
            # print(word + " is human " + h)
            return True
    return False


def refactor_word(word):
    """
    Transforms a systran-like name (with multiple words),
    Ex : Sepp_+_Blatter, into a ConceptNetwork-like name,
    Ex : sepp_blatter.
    """
    return word.lower().replace('_+_', '_').replace(' ', '_')


def reduce_names(sentences, concepts_network=None):
    """
    Recognize composed names, using the concepts network.

    We transform a succession of proper nouns into one single word.
    Words id are not changed in the process. Therefore, all functions
    using words ids should handle the case of a reference to an
    unexisting word.

    @param sentences Sentences parsed from Systran data.
    @param concepts_network ConceptNetwork object (optional). If it exists,
    we will check whether composed names are in the ConceptNetwork or not.
    If it is None, we will just consider that any succession of words
    (tagged as propernoun) has to be reduced into one single name.
    @warning The reduction is done on the data itself
    (words are destroyed in the process).
    """
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
                if concepts_network:
                    if concepts_network.has_node(refactor_word(temp + "_+_" + w["name"])):
                        sentence["words"][w_id]["name"] = temp + "_+_" + w["name"]
                        del sentence["words"][w_id + 1: w_id + 1 + skip]
            elif temp:
                if not concepts_network:
                    sentence["words"][w_id - skip2 - skip]["name"] = temp
                    for w in sentence["words"][w_id - skip - skip2 + 1: w_id - skip2]:
                        for tag in w["tags"]:
                            sentence["words"][w_id - skip2 - skip]["tags"][tag] = w["tags"][tag]
                    del sentence["words"][w_id - skip - skip2 + 1: w_id - skip2]
                skip2 += skip - 1
                skip = 0
                temp = ""


def match_entities(sentences, concepts_network=None):
    """
    @brief Get the entire name of any entity in the text.

    Entities that appear in a sentence are linked together and
    to entities in the conceptsNetwork.

    @param concepts_network conceptsNetwork. It should not be None, in order
    to run a search among nodes.
    @param activate If set to True, we will run a deeper check by activating
    nodes (not useful, deprecated).

    @param sentence A sentence, parsed with the systran parser.
    * {"words": [{...}, {...}, {...}], "text": "...", "id": 6}
    Where each word has the form :
    * {"type": ..., "tags": {...}, "name": ..., "norm": ..., "id": ...}

    @return A dict of id : entity in the ConceptNetwork (or name
    itself if this entity doesn't exist). Id refers to the entity.
    It is a double id, that is,
    sentence id and word id in the sentence.
    """
    # create the dictionary and initialize each entitie's normal form
    names_dict = {}
    for sentence in sentences:
        for w in sentence["words"]:
            if w["type"] in NAMES_TYPES:
                names_dict[(sentence["id"], w["id"])] = refactor_word(w["name"])

    # match in the concepts_network (search for existing nodes)
    matched = list()
    to_match = sorted(list(names_dict.keys()))
    for id in names_dict:
        if concepts_network.has_node(names_dict[id]):
            to_match.remove(id)
            matched.append(id)
    matched.sort()
    to_match.sort()

    # match names together
    # Any name that is contained in another
    # (for example, blatter is in sepp_blatter)
    # is considered as a reference to this one.
    to_match2 = to_match.copy()
    matched2 = matched.copy()
    for i in to_match2:
        for j in matched2:
            if names_dict[i] in names_dict[j] and j < i:
                names_dict[i] = names_dict[j]
                if i not in matched:
                    matched.append(i)
                    to_match.remove(i)
    matched.sort()
    to_match.sort()

    return names_dict


def print_entities_matching(sentences):
    """
    Pretty printing of the entities matching.

    This function allows the user to run some tests
    on data samples.
    """
    entities = match_entities(sentences)
    for s in sentences:
        for w in s["words"]:
            i = (s["id"], w["id"])
            if i not in entities:
                print(s["words"][i[1]]["name"], end=" ")
            else:
                print(s["words"][i[1]]["name"] + " ( " + entities[i] + " ) ", end="")
        print("\n")


def match_and_replace(sentences, cn=None):
    """
    Do all operations.

    Reducing names, matching entities and adding
    new information.
    The sentences are modified themselves (result is None).

    @param sentences Systran-parsed sentences.
    @param cn If not provided (None), the ConceptNetwork is
    loaded from its default location.
    @see DEFAULT_CN
    """
    if cn:
        concepts_network = cn
    else:
        concepts_network = ConceptNetwork()
        print("Loading CN...")
        concepts_network.load(DEFAULT_CN)
        print("Loading complete !")
    reduce_names(sentences)
    entities_dict = match_entities(sentences, concepts_network)
    # replacing names and adding information
    for full_id in entities_dict:
        w = get_word(full_id, sentences)
        w["name"] = entities_dict[full_id]
        if is_human(entities_dict[full_id], concepts_network):
            get_word(full_id, sentences)["tags"]["HUMAN"] = "1"
