"""@file tokenizer.py
@brief Tokenizers.

We need several tokenizers to perform information retrieval from texts.
Those tokenizers may adapt to the errors we find n our data
(for example with the articles from the crawler).
Thus, some of them may be unuseful, even bad, for other sets of data.
"""

from nltk import word_tokenize, pos_tag

####################
# Punctuation
################

PUNKT2 = ",;/!?:"
PUNKT = (";.,?!:_()'/’\u2019()[]=")

#######################
# Characters to always remove
##########################
ALWAYS_REMOVE = "=\t\""

########################
# Sentence boundaries.
########################

BOUNDARIES = ["!", ".", "?", "\n", "'"]

##########################
# Crawler sentences boundaries.
#########################

CRAWLER_BOUNDARIES = ["!", ".", "?", "\n", ":"]


def tokenize(text):
    """
    Split a text into tokens (words, morphemes, names and punctuation).
    """
    return custom_word_tokenize(_refactor(text))


_ALWAYS_REPLACE = {"Mc.": "Mc", "M.": "M", "Mr.": "Mr", "Mrs.": "Mrs"}


def _refactor(text):
    res = text
    for c in ALWAYS_REMOVE:
        res = res.replace(c, " ")
    for w in _ALWAYS_REPLACE:
        res = res.replace(w, _ALWAYS_REPLACE[w])
    return res


def refactor_crawler(text):
    """
    @brief Refactor crawler data.

    The text data from the crawler has several problems :
    * Titles without space, as in :
    "...in the Capital One CupThe semi-final..." which is
    in fact two sentences, has to be cut between "Cup" and "The".
    * Too much spaces and tabulations.
    * punctuation sometimes remains at the beginning.
    * we want to add a dot at the end of the sentence.

    This function intends to make the data useful, for some natural language
    tools (for example Systran's tools).

    @param text Raw text data (str or any character iterable).
    @return A list of sentences (str).
    """
    temp = []
    sents = []
    car2 = ' '
    for car in _refactor(text):
        if (car.isupper() and car2.islower()):
            l = (''.join(temp)).split(' ')
            if l[len(l) - 1] not in ["Mc", "M", "Mr", "Ms", "Mrs"]:
                sents.append(''.join(temp))
                temp = []
            temp.append(car)
        elif (car == ' ' and car2 == ' '):
            sents.append(''.join(temp))
            temp = []
        elif car not in CRAWLER_BOUNDARIES:
            temp.append(car)
        else:
            sents.append(''.join(temp))
            temp = []
        car2 = car
    for sent in sents:
        for p in PUNKT2:
            sent = sent.replace(p, p + " ")
        while sent and not sent[0].isalpha():
            sent = sent[1:]
        if sent and sent[len(sent) - 1].isalpha():
            sent = sent + '.'
        sent2 = sent.replace(" ", "")
        if sent2 != "":
            yield sent


def tokenize_and_tag(text):
    """
    Tokenizes, tags words in a text and yield its sentences.
    Each sentence is a list of words, without punctuation.
    All words are kept, including : remaining punctuation, digits,
    small words or letters.

    @see PUNKT

    @param text Raw text data (str).
    @return Yields a list of lists of [word,POS].
    """
    for sent in refactor_crawler(text):
        sent2 = sent
        # for i in MAJ:
        #    sent2 = sent2.replace(i, " " + i)
        for i in PUNKT:
            sent2 = sent2.replace(i, " ")
        split = word_tokenize(sent2)
        yield (pos_tag(split))


def custom_sent_tokenize(text):
    """
    Custom sentence tokenizer.

    @param text Raw text data (str or any character iterable).
    @return A list of sentences (str).
    """
    temp = []
    sents = []
    car2 = ' '
    for car in text:
        if (car.isupper() and car2.islower()):
            sents.append(''.join(temp))
            temp = []
            temp.append(car)
        elif car not in BOUNDARIES:
            temp.append(car)
        else:
            sents.append(''.join(temp))
            temp = []
        car2 = car
    return sents


def custom_word_tokenize(text):
    """
    Tokenizer which recognizes named_entities,
    and keeps the order of the words.
    """
    words = []
    for sent in custom_sent_tokenize(text):
        split = word_tokenize(sent)
        tokens = pos_tag(split)
        temp = []
        for key, val in tokens:
            if val == 'NNP':
                temp.append(key)
            else:
                if temp:
                    words.append(' '.join(temp))
                    temp = []
                words.append(key)
        if temp:
            words.append(' '.join(temp))
            temp = []
    return words


if __name__ == "__main__":
    pass
