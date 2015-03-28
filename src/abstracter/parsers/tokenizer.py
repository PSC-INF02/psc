"""@file tokenizer.py
Tokenizers.
"""
from nltk import word_tokenize, pos_tag


PUNKT = (";.,?!:_()'/’\u2019()[]=")
ALWAYS_REMOVE = "=\t\""
BOUNDARIES = ["!", ".", "?", "\n", "'"]
CRAWLER_BOUNDARIES = ["!", ".", "?", "\n", ":"]


def tokenize(text):
    """
    Split a text into tokens (words, morphemes, names and punctuation).
    """
    return custom_word_tokenize(_refactor(text))


def _refactor(text):
    res = text
    for c in ALWAYS_REMOVE:
        res = res.replace(c, " ")
    return res


def refactor_crawler(text):
    """
    Refactor crawler data.

    The text data from the crawler has several problems :\n
    -Titles without space, as in :
    "...in the Capital One CupThe semi-final..." which is
    in fact two sentences, has to be cut between "Cup" and "The".\n
    -Too much spaces and tabulations.\n
    -punctuation sometimes remains at the beginning.\n
    -we want to add a dot at the end of the sentence.\n
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
    _text = """Peyton Manning will have a new left tackle protecting his blindside after the Denver Broncos placed Ryan Clady on season-ending injured reserve Wednesday.

Clady hurt his left foot Sunday when New York Giants defensive lineman Cullen Jenkins rolled up on him while the Broncos were trying to run out the clock in their 41-23 win. Clady will soon undergo surgery for what's being called a Lisfranc tear, which involves a separation of ligaments and joints in the foot.

Chris Clark, a fifth-year journeyman, will take the place of Clady - the undisputed leader on the line - and make his first career start at left tackle Monday night when the Broncos (2-0) host the Oakland Raiders (1-1).

''Stepping up into a role like this, it's not going to be hard for me to adjust,'' said Clark, who received a two-year contract extension on Monday. ''It's not about filling a guy's shoes for me. It's about me creating my legacy, just helping the team the best way I can and doing my job.''

Still, those are some big cleats for Clark to fill.
"""

    for w in (tokenize_and_tag(_text)):
        print(w)
