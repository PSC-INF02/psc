"""@file api.py
API for Conceptnet5.

Conceptnet5 supports 3 API :
* LookUp
* Search (searching for edges)
* Association (get similarity between concepts)

Lookup is for when you know the URI of an object in ConceptNet,
and want to see a list of edges that include it.
Search finds a list of edges that match certain criteria.
Association is for finding concepts similar
to a particular concept or a list of concepts.

@warning These methods are mostly unused since the
introduction of concurrent requests.

@see concurrent_api.py For concurrent requests, a gain of time.
@see result.py For parsing queries result.
"""

import urllib.parse
from abstracter.conceptnet5_client.result import parse_relevant_edges, parse_similar_concepts
from abstracter.util.http import make_http_request
import abstracter.conceptnet5_client.settings as settings


def search_concept(concept, limit=1, **kwargs):
    '''
    Performs a lookup query and parses the result into edges objects.
    @see result.py
    @see settings.SUPPORTED_LOOKUP_ARGS

    @param concept  A concept, word or phrase, e.g. 'toast', 'see movie' etc.
    @param limit    The number of results needed.
    @param kwargs Other supported lookup arguments.
    @return A list of result.Edge objects.
    '''
    query_args = {"limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_LOOKUP_ARGS:
            query_args[key] = value
        else:
            raise Exception("LookUp argument '" + key + "' incorrect.")
    enc_query_args = urllib.parse.urlencode(query_args)
    concept = concept.replace(' ', '_')
    url = ''.join(['%s/c/%s/%s?' % (settings.BASE_LOOKUP_URL, settings.LANGUAGE, concept)]) + enc_query_args
    json_data = make_http_request(url).json()
    return parse_relevant_edges(json_data)


def get_similar_concepts(concept='dog', filter='/c/en/', limit=10, **kwargs):
    """
    Performs an association query and parses the result.
    @see settings.SUPPORTED_ASSOCIATION_ARGS

    @param concept Word or phrase.
    @param filter Filter.
    @param limit Maximum number of results.
    @param kwargs Other supported association arguments.
    @return A list of [concept,similarity].
    """
    query_args = {"filter": filter, "limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_ASSOCIATION_ARGS:
            query_args[key] = value
        else:
            raise Exception("Association argument '" + key + "' incorrect.")
    enc_query_args = urllib.parse.urlencode(query_args)
    url = ''.join(['%s/c/%s/%s?' % (settings.BASE_ASSOCIATION_URL,
                                    settings.LANGUAGE, concept)]) + enc_query_args
    json_data = make_http_request(url)
    return parse_similar_concepts(json_data)


def get_similarity(concept1='dog',concept2='dog'):
    """
    Performs an association query and gets a similarity score between two concepts.

    @param concept1 First concept.
    @param concept2 Second concept.
    @return A similarity score (float).
    """
    query_args = {"filter": '/c/' + settings.LANGUAGE + "/" + concept2}
    enc_query_args = urllib.parse.urlencode(query_args)
    url = ''.join(['%s/c/%s/%s?' % (settings.BASE_ASSOCIATION_URL, settings.LANGUAGE,concept1)]) + enc_query_args
    json_data = make_http_request(url)
    parsed = parse_similar_concepts(json_data)
    if parsed:
        return parsed[0][1]
    else:
        return 0



def get_similar_concepts_by_term_list(term_list, filter='/c/en/', limit=10, **kwargs):
    """
    Returns concepts similar to the list.
    Example : http://conceptnet5.media.mit.edu/data/5.3/assoc/list/en/wayne_rooney,sport
    """
    terms = ','.join(term_list)
    query_args = {"filter": filter, "limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_ASSOCIATION_ARGS:
            query_args[key] = value
        else:
            raise Exception("Association argument '" + key + "' incorrect.")
    enc_query_args = urllib.parse.urlencode(query_args)
    url = ''.join(['%s/list/%s/%s?' % (settings.BASE_ASSOCIATION_URL, settings.LANGUAGE, terms)]) + enc_query_args
    json_data = make_http_request(url)
    return parse_similar_concepts(json_data)


def search_edges(filter='/c/en/', limit=10, **kwargs):
    """
    Performs a search query and parses the result.
    @see settings.SUPPORTED_SEARCH_ARGS

    @param filter Filter.
    @param limit Maximum number of results.
    @param kwargs Other supported search arguments.
    @return A list of result.Edge objects.
    """
    query_args = {"filter": filter, "limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_SEARCH_ARGS:
            query_args[key] = value
        else:
            raise Exception("Search argument '" + key + "' incorrect.")
    enc_query_args = urllib.parse.urlencode(query_args)
    url = ''.join(['%s%s' % (settings.BASE_SEARCH_URL, '?')]) + enc_query_args
    json_data = make_http_request(url)
    return parse_relevant_edges(json_data)


def search_edges_from(concept='dog'):
    """
    Simple method to search edges starting from a concept.
    """
    return search_edges(start='/c/' + settings.LANGUAGE + '/' + concept, minWeight=2)


def search_edges_to(concept='dog'):
    """
    Simple method to search edges going to a concept.
    """
    return search_edges(end='/c/' + settings.LANGUAGE + '/' + concept, minWeight=2)


def search_edge(start, end):
    """
    Search one edge only, which starts at start and
    ends at end.
    """
    edges = search_edges(start='/c/' + settings.LANGUAGE + '/' + start,
                         end='/c/' + settings.LANGUAGE + '/' + end)
    if edges:
        return edges[0]
