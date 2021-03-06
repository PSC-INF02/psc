"""Client for freebase queries.

The settings are put in a file settings.py, which has to contain
the data in file default_settings.py, with a real google api key.
"""
import urllib.parse
from abstracter.freebase_client.settings import USER_KEY, URL, SEARCH_PARAMETERS, MINIMUM_RESULT_SCORE
from abstracter.util.http import make_https_request
import abstracter.util.concurrent as co


def keep_relevant(query_response):
    """
    Keep only relevant results (unused).

    @param query_response The response to a query, already transformed
    via the .json() method.
    """
    for result in query_response['result']:
        if result['score'] > MINIMUM_RESULT_SCORE:
            yield result


def search(lang='en', limit=10, **kwargs):
    """
    Search freebase.

    @param kwargs Any relevant search parameters.
    @return The response to the query, encoded in JSON.

    Example :
    @code
    search(query='barack_obama',lang='en',
        filter='(any type:/people/person)',limit=2,exact=True)
    search(filter='(all type:/people/person member_of:france)',
        limit=10,exact=False)
    search(filter='(all discovered_by:heisenberg)',limit=10)
    for i in (search(query='ezequiel lavezzi',lang='en',
        filter='(any type:/people/person)',limit=2)):
            print(i)
    @endcode
    """
    data = {'key': USER_KEY, 'lang': lang, 'limit': limit}
    for key, val in kwargs.items():
        if key in SEARCH_PARAMETERS:
            data[key] = val
        else:
            pass
    url_values = urllib.parse.urlencode(data)
    full_url = URL + '?' + url_values
    resp = make_https_request(full_url).json()
    return resp['result']


def search_name(name):
    """
    Searches a name in Freebase and returns only very few results.

    The goal is to know only what a name refers to.

    @param name A name (str).

    Examples :
    @code
    search_name("albert rusnak")
    @endcode
    """
    data = search(query=name, lang='en', limit=2)
    res = {}
    if data:
        dat = data[0]
        score = dat['score']
        name = dat['name']
        res['from'] = name.lower().replace(' ', '_')
        res['score'] = score
        if 'notable' in dat:
            res['to'] = dat['notable']['name'].lower().replace(' ', '_')
            # IsA relation
    return res


def search_name_url(name, **kwargs):
    """
    Returns the url of a search query which goal is to know
    what a name refers to.

    @return An url (str).
    """
    data = {'query': name, 'key': USER_KEY, 'lang': 'en', 'limit': 2}
    for key, val in kwargs.items():
        if key in SEARCH_PARAMETERS:
            data[key] = val
        else:
            pass
    url_values = urllib.parse.urlencode(data)
    return URL + '?' + url_values


def search_names(names, **kwargs):
    """
    Performs a number of concurrent requests of search_name type.

    @param names A list of names to search for. They can be written with
    underscores (like "wayne_rooney") or without ("wayne rooney").
    Spaces will be replaced with underscores.
    @return A dict containing, for each name,
    the query result parsed with parse_results.

    @see util.concurrent.py
    """
    urls = {}
    for name in names:
        urls[name] = search_name_url(name.replace(' ', '_'), **kwargs)
    return co.requests(urls, parsing_method=parse_results)


def parse_results(query_result):
    """
    @param query_result A query result, encoded in JSON.
    @return A dict representing the query result,
    with keys 'from', 'score', maybe 'to'.
    """
    res = {}
    data = query_result['result']
    if data:
        dat = data[0]
        score = dat['score']
        name = dat['name']
        res['from'] = name.lower().replace(' ', '_')
        res['score'] = score
        if 'notable' in dat:
            res['to'] = dat['notable']['name'].lower().replace(' ', '_')
            # IsA relation
    return res


if __name__ == "__main__":
    print(search_name("albert rusnak"))
