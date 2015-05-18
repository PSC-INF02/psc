"""@file anaphora_resolution.py

@brief Resolve anaphoras in a text.

The problem of anaphora resolution is the following : we want
to discover which name or noun phrase a pronoun refers to.

This package uses the Systran parser, but it can be adapted to
other syntax parsing tools, as soon as
the json data provided contains enough information (such as types and tags).

@see grammar.systran_parser.py
@see grammar.grammartree.py
"""
from abstracter.grammar.utils import PRONOUN_TAGS, NON_REFERENTIAL_PRONOUNS, INDEFINITE, PROPERNOUNS

PREV_SENTS = 5
NEXT_SENTS = 1
def resolve_anaphoras(tree):
    """
    Resolve anaphoras i.e. find a noun phrase corresponding to each pronoun.

    The algorithms expects the input tree to have the following structure:
    tree = [paragraph, ...]
    paragraph = [sentence | punctuation, ...]
    sentence = [noun_phrase | other, ...]
    """
    pronouns = list(x for x in tree.leaves() if x['kind'] in PRONOUN_TAGS and x['norm'] not in NON_REFERENTIAL_PRONOUNS)
    noun_phrases = list(tree.nodes(kind='noun_phrase'))
    # Sort noun phrases by order in text
    noun_phrases.sort(key=lambda np: np.path()[:2] + [np['global_id']])

    # for each pronoun
    scores = []
    for i, pron in enumerate(pronouns):
        pron_path = pron.path()
        scores.append([])
        # for each noun phrase
        for j, np in enumerate(noun_phrases):
            np_path = np.path()
            np_score = 0

            # Proximity between noun phrase and pronoun
            global_id_delta = pron['global_id'] - np['global_id']
            sent_delta = pron.root[pron_path[:2]]['global_sent_id'] - np.root[np_path[:2]]['global_sent_id']

            if not (-PREV_SENTS < -sent_delta < NEXT_SENTS):
                np_score -= 100 * abs(sent_delta)

            # the noun phrase probably has to appear before the pronoun
            if global_id_delta < 0:
                np_score -= 100
            elif sent_delta != 0:
                np_score -= sent_delta * 8
            else:
                np_score -= global_id_delta * 0.5

            # plural or singular
            if 'NUMBER' in pron['tags'] and 'NUMBER' in np['tags']:
                if pron['tags']['NUMBER'] == pron['tags']['NUMBER']:
                    np_score += 10
                else:
                    np_score -= 100

            # human or not human
            if 'HUMAN' in pron['tags'] and 'HUMAN' in np['tags']:
                if pron['tags']['HUMAN'] == pron['tags']['HUMAN']:
                    np_score += 10
                else:
                    np_score -= 30

            scores[-1].append(np_score)

    # 1: noun phrases that appear at the beginning of a sentence
    # get a better score
    crnt_sentence = None
    for j, np in enumerate(noun_phrases):
        np_path = np.path()
        if crnt_sentence != np_path[:2]:  # New sentence
            crnt_sentence = np_path[:2]
            for i in range(len(scores)):
                scores[i][j] += 5


    # 2 : lexical reiteration (with previous sentences also)
    # each repeated head noun gets a better score
    head_noun_map = {}
    for j, np in enumerate(noun_phrases):
        if 'HEAD_NOUN' not in np['tags']:
            continue
        head_noun_text = np.root[np['tags']['HEAD_NOUN']]['text'].lower()
        if head_noun_text not in head_noun_map:
            head_noun_map[head_noun_text] = []
        head_noun_map[head_noun_text].append(j)

    for k, l in head_noun_map.items():
        if len(l) >= 2:
            for j in l:
                for i in range(len(scores)):
                    scores[i][j] += 5

    # 3 : prepositional or non prepositional NP : "into the VCR"
    # + ranking : subject, direct object, indirect object
    # definite noun phrases also
    for j, np in enumerate(noun_phrases):
        delta = 0
        # prepositional Noun phrases
        if np['tags'].get("MODIFIED_BY_PREP1") is not None:
            delta -= 2
        if np['tags'].get("AGENT_OF_VERB") is not None:
            delta += 10
        if np['tags'].get("OBJECT_OF_VERB") is not None:
            delta -= 2
        if np['tags'].get("DIROBJ_OF") is not None:
            delta -= 10
        # indefinite (contains an indefinite article)
        if any(x["norm"] in INDEFINITE for x in np if "norm" in x):
            delta -= 10
        # propernoun
        if 'HEAD_NOUN' in np['tags']:
            head_noun = np.root[np['tags']['HEAD_NOUN']]
            if head_noun['kind'] in PROPERNOUNS:
                delta += 10

        if delta != 0:
            for i in range(len(scores)):
                scores[i][j] += delta

    # 4 : collocation pattenrn

    # 5 :immediate reference

    # 6 : term preference

    # get the best
    for i, pron in enumerate(pronouns):
        j = max(enumerate(scores[i]), key=lambda x:x[1])[0]
        np = noun_phrases[j]
        pron['tags']['REFERS_TO'] = np.path()
