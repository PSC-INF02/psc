"""@file retriever.py
Functions to retrieve concepts and names from a text.

Includes tokenizing, tagging.
"""

import abstracter.parsers.normalizer as norm
import abstracter.parsers.tokenizer as tok
import re



USEFUL_TAGS=["JJ","NN","NNS","VB","VBD","VBG","VBN","VBP","VBZ"];

NOT_USEFUL_TAGS=["CC","NNP","NNPS","RB","RBR","RBS","JJR","JJS","MD"]
#R : adverbs
#J : adjectives
#V : verbs
#N : nouns
# 1.  CC    Coordinating conjunction
# 2.    CD  Cardinal number
# 3.    DT  Determiner
# 4.    EX  Existential there
# 5.    FW  Foreign word
# 6.    IN  Preposition or subordinating conjunction
# 7.    JJ  Adjective
# 8.    JJR Adjective, comparative
# 9.    JJS Adjective, superlative
# 10.   LS  List item marker
# 11.   MD  Modal
# 12.   NN  Noun, singular or mass
# 13.   NNS Noun, plural
# 14.   NNP Proper noun, singular
# 15.   NNPS    Proper noun, plural
# 16.   PDT Predeterminer
# 17.   POS Possessive ending
# 18.   PRP Personal pronoun
# 19.   PRP$    Possessive pronoun
# 20.   RB  Adverb
# 21.   RBR Adverb, comparative
# 22.   RBS Adverb, superlative
# 23.   RP  Particle
# 24.   SYM Symbol
# 25.   TO  to
# 26.   UH  Interjection
# 27.   VB  Verb, base form
# 28.   VBD Verb, past tense
# 29.   VBG Verb, gerund or present participle
# 30.   VBN Verb, past participle
# 31.   VBP Verb, non-3rd person singular present
# 32.   VBZ Verb, 3rd person singular present
# 33.   WDT Wh-determiner
# 34.   WP  Wh-pronoun
# 35.   WP$ Possessive wh-pronoun
# 36.   WRB Wh-adverb


_digits = re.compile('\d')
def _contains_digits(d):
    return bool(_digits.search(d))

def _links_to(entity_list,name):
    """
    Return the whole name of sth or sb, given the list of entities in the text.
    For example, Wayne in the list ["Wayne Rooney", "Tom"] refers obviously to "Wayne Rooney".
    We thus avoid taking a Family Name or a First Name for the whole name.

    @param entity_list List of entities (string).
    @param name A name (string).
    @return A full name (string).
    """
    if entity_list:
        temp=name
        for e in entity_list:
            if temp in e:
                temp=e
        return temp
    return None


def get_names(sents):
    """
    Get all named entities in previously tagged sentences.

    @param sents Generator of tagged sentences (list of [word,POS])
    @return A list of named entities.
    """
    named_entities=[]
    for sent in sents:
        temp=[]
        for key,val in sent:
            if val=='NNP':
                temp.append(key)
            else:#end of name
                if temp:
                    named_entities.append(' '.join(temp))
                temp=[]
    return named_entities    

def get_important_words(sents):
    """
    Get all important words in a list of previously tagged sentences.
    Dismiss one letter words, dismiss prepositions...
    @see USEFUL_TAGS

    @param sents Generator of tagged sentences (list of [word,POS])
    @return Generator of tagged sentences (list of [word,POS])
    """
    for sent in sents:
        for key,val in sent:
            if val in USEFUL_TAGS and not _contains_digits(key) and len(key)>1:
                yield ([key,val])


def retrieve_words_only(sents):
    """
    We retrieve words in their normal form and count their occurrences in a dictionary.
    Thus, if a concept is used n times, it is counted n times.

    @param sents Generator of tagged sentences (list of [word,POS]).
    @return List of concepts (string).
    """
    words=norm.normalize(get_important_words(sents))
    concepts={}
    for word in words:
        if word in concepts:
            concepts[word]+=1
        else:
            concepts[word]=1
    #return the dictionary
    return concepts


def retrieve_names_only(sents):
    """
    Retrieve names and count their occurrences in a dictionary.\n
    Thus, if a name is used n times, it is counted n times.

    @param sents Generator of tagged sentences (list of [word,POS]).
    @return List of names (string).

    @todo : améliorer ça...
    """
    names=list(s.lower() for s in get_names(sents))
    res={}
    for name in names:
        name2=_links_to(names,name)
        if not name2 in res:
            res[name2]=1
        else:
            res[name2]=res[name2]+1
    return res 


def retrieve_words_names(text):
    """
    Retrieve words and names of a text.
    Returns a tuple of two dicts : words (not -proper noun concepts) and names.
    
    @param text The text to analyze (string).
    @return A tuple of two dicts : [words,names].
    """
    sents=list(tok.tokenize_and_tag(text))
    return [retrieve_words_only(sents),retrieve_names_only(sents)]