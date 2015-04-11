"""@file concurrent_api.py
Concurrent API for Conceptnet5.

Conceptnet5 supports 3 API :\n
-LookUp\n
-Search (searching for edges)\n
-Association (get similarity between concepts)\n
Lookup is for when you know the URI of an object in ConceptNet,
and want to see a list of edges that include it.
Search finds a list of edges that match certain criteria.
Association is for finding concepts similar
to a particular concept or a list of concepts.

@see api For simple, non-concurrent queries.
@see result.py For parsing queries result.
"""

import urllib.parse
import abstracter.util.concurrent as co
from abstracter.conceptnet5_client.result import parse_relevant_edges, parse_similar_concepts
import abstracter.conceptnet5_client.settings as settings


def lookup_url(concept, filter='/c/en/', limit=10, **kwargs):
    """
    Returns the url for a lookup query.
    @see settings.SUPPORTED_LOOKUP_ARGS

    @param filter  Filter applied on results (default value : '/c/en/', english only).
    @param limit   Maximum number of results (default value : 10).
    @param **kwargs  Other supported lookup arguments.
    @return An url (str).
    """
    query_args = {"limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_LOOKUP_ARGS:
            query_args[key] = value
        else:
            raise Exception("LookUp argument '" + key + "' incorrect.")
    concept = concept.replace(' ', '_')
    enc_query_args = urllib.parse.urlencode(query_args)
    return ''.join(['%s/c/%s/%s?' % (settings.BASE_LOOKUP_URL, settings.LANGUAGE, concept)]) + enc_query_args


def search_concepts(concepts, filter='/c/en/', limit=10, **kwargs):
    '''
    Performs lookup queries and parses results into edges objects.
    @see result.py

    @param concepts  Iterable of concepts, words or small phrases.
    @param limit    The number of results needed for each query.
    @param kwargs Other supported lookup arguments, for each query.
    @return A dict which contains, for each concept, a list of result.Edge objects.
    '''
    urls = {}
    for concept in concepts:
        urls[concept] = lookup_url(concept, filter, limit, **kwargs)
    return co.requests(urls, parsing_method=parse_relevant_edges)


def association_url(concept='dog', filter='/c/en/', limit=10, **kwargs):
    """
    Returns the url for an association query.
    @see settings.SUPPORTED_ASSOCIATION_ARGS

    @param concept The concept we want to associate others with.
    @param filter  Filter applied on results (default value : '/c/en/', english only).
    @param limit   Maximum number of results (default value : 10).
    @param **kwargs  Other supported association arguments.
    @return An url (str).
    """
    query_args = {"filter": filter, "limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_ASSOCIATION_ARGS:
            query_args[key] = value
        else:
            raise Exception("Association argument '" + key + "' incorrect.")
    concept = concept.replace(' ', '_')
    enc_query_args = urllib.parse.urlencode(query_args)
    return ''.join(['%s/c/%s/%s?' % (settings.BASE_ASSOCIATION_URL, settings.LANGUAGE,concept)]) + enc_query_args


def get_similar_concepts(concepts, filter='/c/en/', limit=10, **kwargs):
    """
    Performs associations query and parses the results.

    @param concepts Iterable of word or small phrases.
    @param filter Filter.
    @param limit Maximum number of results.
    @param kwargs Other supported association arguments.
    @return A dict which contains, for each concept, a list of [concept,similarity].
    """
    urls = {}
    # we build a dict of url
    for concept in concepts:
        urls[concept] = association_url(concept, filter, limit, **kwargs)
    return co.requests(urls, parsing_method=parse_similar_concepts)


def search_url(filter='/c/en/', limit=10, **kwargs):
    """
    Returns the url for a search query.
    @see settings.SUPPORTED_SEARCH_ARGS

    @param filter  Filter applied on results (default value : '/c/en/', english only).
    @param limit   Maximum number of results (default value : 10).
    @param **kwargs  Other supported search arguments.
    @return An url (str).
    """
    query_args = {"filter": filter, "limit": limit}
    for key, value in kwargs.items():
        if key in settings.SUPPORTED_SEARCH_ARGS:
            query_args[key] = value
        else:
            raise Exception("Search argument '" + key + "' incorrect.")
    enc_query_args = urllib.parse.urlencode(query_args)
    return ''.join(['%s%s' % (settings.BASE_SEARCH_URL, '?')]) + enc_query_args


def search_edges_from(concepts, filter='/c/en/', limit=10, **kwargs):
    """
    Performs search queries with start=concept for each concept in concepts.

    @param concepts Iterable of concepts (word or small phrase) .
    @param filter Filter.
    @param limit Maximum number of results.
    @param kwargs Other supported search arguments.
    @return A dict which contains, for each concept, a list of result.Edge objects.
    """
    # build urls dict
    urls = {}
    for concept in concepts:
        concept = concept.replace(' ', '_')
        urls[concept] = search_url(start='/c/' + settings.LANGUAGE + '/' + concept,
                                   filter=filter, limit=limit, **kwargs)
    return co.requests(urls, parsing_method=parse_relevant_edges)
