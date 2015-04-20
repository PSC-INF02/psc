"""
@file utils.py
@brief Util functions and parameters to treat systran
raw data and itself parsed to json.

In particular, we have here the lists of tags and types
that are considered for anaphora resolution, and the name
of the default ConceptNetwork to be loaded to perform
operations that need it (especially names resolution).
"""


###############################"
#
###############################

VERB_GROUPS_TYPES = ["aux:plain",
                     "verb:inf",
                     "prtcl",
                     "aux:plain_x_aux:inf",
                     "verb:plain_x_adv",
                     "verb:pastpart",
                     "verb:prespart",
                     "aux:plain_x_adv",
                     "aux:pastpart",
                     "verb:plain",
                     "aux:plain_x_aux:pastpart",
                     "aux:prespart",
                     # "verb:plain_x_pron",
                     "aux:inf",
                     "adv_x_aux:plain",
                     "adv",
                     "aux:plain_x_aux:plain"]


MASTER_VERB_TAGS = ["PASSIVE", "PAST", "PERFECT", "PRESENT", "FUTURE", "DIROBJ"]

TO_ADD_VB = ["MODIFIED_BY_ADVERB"]

TO_BE_ADDED_VB = ["MODIFIES"]

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


##########################
# Types of pronouns
############################

PRONOUN_TAGS = ["pron"]


#######################################
# indefinite articles
##############################

INDEFINITE = ["a"]


ANTECEDENT_TAGS = ["ANTECEDENT"]

##############################
# Types of words in noun phrases (systrans's types)
########################

NOUN_PHRASES_TYPES = ["noun:propernoun", "noun:common", "noun:acronym",
                      "det", "adj", "numeric"]

################################
# Types of proper nouns
############################

PROPERNOUNS = ["noun:propernoun", "noun:acronym"]


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


def get_tag(sents, full_id, tag):
    return get_word(full_id, sents)["tags"].get(tag, None)


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


def has_tag_in(word, tag_list):
    for tag in tag_list:
        if tag in word["tags"]:
            return True
    return False


def has_type_in(word, type_list):
    return word["type"] in type_list
