import sys
from abstracter.grammar.utils import *


def group_sentences(paragraph):
    """ Try to group together 'sentences' using punctuation
    input:
    paragraph = [word, ...]

    output:
    paragraph = [sentence | punctuation, ...]
    sentence = [word, ...]
    """
    sentence_eq = [[]]
    for w in paragraph:
        if w['text'] in ['.', '\"', ':']:
            sentence_eq.append([])
        else:
            sentence_eq[-1].append(w.id)
    paragraph.group_words(sentence_eq, kind='sentence')


# def group_phrases(sentence):
#     """ Group any connected words into 'phrases'
#     """
#     any_eq = []
#     for w in sentence.leaves():
#         any_eq.append([sentence.subpath(path)[0] for _, path in w.relation_tags()] + [w.id])
#     # Add words in-between
#     # for e in any_eq:
#     #     e.sort()
#     # any_eq = [list(range(e[0], e[-1])) for e in any_eq]
#     sentence.group_words(any_eq, kind='phrase')


def group_compound_propernouns(sentence):
    """ Group compound propernouns
    """
    propernoun_eq = []
    for w in sentence:
        if w['type'] in PROPERNOUNS:
            for tag, path in w.relation_tags():
                if tag in PROPERNOUNS_RELATIONS:
                    try:
                        propernoun_eq.append([w.id, sentence.subpath(path)[0]])
                    except IndexError as ex:  # target is not in the same sentence
                        print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'compound_propernoun', str(ex)), file=sys.stderr)

    propernouns = sentence.group_words(propernoun_eq, kind='compound_propernoun', merge_tags=True)
    for n in propernouns:
        if any(w['tags'].get('HUMAN') for w in n):
            n['tags']['HUMAN'] = True


def group_noun_phrases(sentence):
    """ Group noun phrases
    """
    noun_phrases_eq = []
    head_nouns = set()
    for w in sentence:
        if w['kind'] in NOUN_PHRASE_TYPES and not set(HEAD_NOUN_TAGS).isdisjoint(w['tags']):
            head_nouns.add(w.id)
            eq = [w.id]
            for tag in RELATED_FROM_HEAD_NOUN_TAGS:
                target = w['tags'].get(tag)
                if target is not None and w.root[target]['kind'] in NOUN_PHRASE_TYPES:
                    try:
                        eq.append(sentence.subpath(target)[0])
                    except IndexError as ex:  # target is not in the same sentence
                        print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'noun_phrase', str(ex)), file=sys.stderr)
            noun_phrases_eq.append(eq)

    for w in sentence:
        if w['kind'] in NOUN_PHRASE_TYPES:
            for tag in RELATED_TO_HEAD_NOUN_TAGS:
                target = w['tags'].get(tag)
                if target is not None:
                    try:
                        target = sentence.subpath(target)[0]
                        if target in head_nouns:
                            noun_phrases_eq.append([w.id, target])
                    except IndexError as ex:  # target is not in the same sentence
                        print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'noun_phrase', str(ex)), file=sys.stderr)

    noun_phrases = sentence.group_words(noun_phrases_eq, kind='noun_phrase', merge_tags=True)
    for np in noun_phrases:
        head_nouns = []
        for w in np:
            if w['kind'] in NOUN_PHRASE_TYPES and not set(HEAD_NOUN_TAGS).isdisjoint(w['tags']):
                head_nouns.append(w)

        if len(head_nouns) != 1:
            print("Noun phrase '%s' has multiple possible head nouns: %s" % (np['text'], ', '.join("'%s'" % w['text'] for w in head_nouns)), file=sys.stderr)
            continue
        head_noun = head_nouns[0]

        np['tags']['HEAD_NOUN'] = head_noun.path()
        head_noun['tags']['IS_HEAD_NOUN'] = True
        # Copy relevant tags from head noun
        for t in head_noun['tags']:
            if t not in np['tags'] or t in ['NUMBER']:
                np['tags'][t] = head_noun['tags'][t]


def group_verb_phrases(sentence):
    """ Group verb phrases
    """
    verb_phrases_eq = []
    head_verbs = set()
    for w in sentence:
        if w['kind'] in VERB_PHRASE_TYPES and not set(HEAD_VERB_TAGS).isdisjoint(w['tags']):
            head_verbs.add(w.id)
            eq = [w.id]
            for tag in RELATED_FROM_HEAD_VERB_TAGS:
                target = w['tags'].get(tag)
                if target is not None and w.root[target]['kind'] in VERB_PHRASE_TYPES:
                    try:
                        eq.append(sentence.subpath(target)[0])
                    except IndexError as ex:  # target is not in the same sentence
                        print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'noun_phrase', str(ex)), file=sys.stderr)

            verb_phrases_eq.append(eq)

    for w in sentence:
        if w['kind'] in VERB_PHRASE_TYPES:
            for tag in RELATED_TO_HEAD_VERB_TAGS:
                target = w['tags'].get(tag)
                if target is not None:
                    try:
                        target = sentence.subpath(target)[0]
                        if target in head_verbs:
                            verb_phrases_eq.append([w.id, target])
                    except IndexError as ex:  # target is not in the same sentence
                        print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'verb_phrase', str(ex)), file=sys.stderr)


    verb_phrases = sentence.group_words(verb_phrases_eq, kind='verb_phrase', merge_tags=True)
    for vp in verb_phrases:
        head_verbs = []
        for w in vp:
            if w['kind'] in VERB_PHRASE_TYPES and not set(HEAD_VERB_TAGS).isdisjoint(w['tags']):
                head_verbs.append(w)

        if len(head_verbs) != 1:
            print("Verb phrase '%s' has multiple possible head verbs: %s" % (vp['text'], ', '.join("'%s'" % w['text'] for w in head_verbs)), file=sys.stderr)
            continue
        head_verb = head_verbs[0]

        vp['tags']['HEAD_VERB'] = head_verb.path()
        head_verb['tags']['IS_HEAD_VERB'] = True
        # Copy relevant tags from head verb
        for t in head_verb['tags']:
            if t not in vp['tags'] or t in ['PERSONS']:
                vp['tags'][t] = head_verb['tags'][t]


def group_syntagmes(sentence):
    """ Group syntagmes, using relations in the 'relations' atribute
    """
    syntagmes_eq = []
    for w in sentence.leaves():
        if 'relations' in w:
            eq = []
            for rel in w["relations"]:
                try:
                    eq.append(sentence.subpath(rel)[0])
                except IndexError as ex:  # target is not in the same sentence
                    print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'syntagme', str(ex)), file=sys.stderr)
            syntagmes_eq.append(eq)
            del w['relations']

    sentence.group_words(syntagmes_eq, kind='syntagme')



def group_grammartree(gtree):
    """
    Transforms a flat grammar tree (which knows only paragraphs) into a deeper
    nested structure, by recognizing several grammatical constructs.

    The resulting tree has the following structure:
    tree = [paragraph, ...]
    paragraph = [sentence | punctuation, ...]
    sentence = [syntagme | noun_phrase | verb_phrase | word, ...]
    syntagme = [noun_phrase | verb_phrase | word, ...]
    word = a leaf of the input tree, or a compound_propernoun
    """

    for paragraph in gtree:
        group_sentences(paragraph)

        for sentence in paragraph.nodes(depth=1, kind='sentence'):
            group_compound_propernouns(sentence)
            group_noun_phrases(sentence)
            group_verb_phrases(sentence)
            group_syntagmes(sentence)
