"""@file ettings.py
@brief A number of settings to work with conceptnet5.

Including base urls, queries arguments.

@see api.py
@see concurrent_api.py
"""

####################################
# Default language
#####################################

LANGUAGE = "en"


##############################################
# These URLs basically points to MIT's conceptnet5 setup for Web API
###################################################

BASE_LOOKUP_URL = 'http://conceptnet5.media.mit.edu/data/5.3'
BASE_SEARCH_URL = 'http://conceptnet5.media.mit.edu/data/5.3/search'
BASE_ASSOCIATION_URL = 'http://conceptnet5.media.mit.edu/data/5.3/assoc'

##############################################
# These are the supported query arguments for LookUp API
# Another one, offset (integer), to skip the specifiec
# amount of first results, seems to have been suppressed in conceptnet5.3.
# @param limit Change the number of results from the default of 50
# @param filter If 'core', only get edges from the ConceptNet 5 Core
# (not from ShareAlike resources), if 'core-assetions', search for edges by default,
# and there can be many edges representing the same assertion.
###################################################
SUPPORTED_LOOKUP_ARGS = ['filter', 'limit']

###################################################
# This is the supported query arguments for Association API
# @param limit Change the number of results from the default of 50.
# @param filter Constrain to return only results that start with the given URI.
# For example, filter=/c/en returns results in English. (It is different from the lookup API!)
####################################################

SUPPORTED_ASSOCIATION_ARGS = ['limit', 'filter']

#######################################
# Supported arguments for Search API
# @param {id, uri, rel, start, end, context, dataset, license} giving
# a ConceptNet URI for any of these parameters will return edges whose
# corresponding fields start with the given path. Type : URI.
# @param nodes Returns edges whose rel, start, or end start with the given URI.
# @param {startLemmas, endLemmas, relLemmas} Returns edges containing the
# given lemmatized word anywhere in their start, end, or rel respectively.
# @param text Matches any of startLemmas, endLemmas, or relLemmas.
# @param surfaceText Matches edges with the given word in their surface text.
# The word is not lemmatized, but it is a case-insensitive match.
# @param minWeight Filters for edges whose weight is at least weight (type : float).
# @param limit Change the number of results from the default of 50.
# @param offset Skip the specified amount of first results.
# @param features Takes in a feature string (an assertion with one open slot),
# and returns edges having exactly that string as one of their features (type : string of uri).
# @param filter If 'core', only get edges from the ConceptNet 5 Core
# (not from ShareAlike resources), if 'core-assetions', search for edges by default,
# and there can be many edges representing the same assertion.
##################################################

SUPPORTED_SEARCH_ARGS = ['id', 'uri', 'rel', 'start',
                         'end', 'context', 'dataset',
                         'license', 'nodes',
                         'startLemmas', 'endLemmas',
                         'relLemmas', 'text',
                         'surfaceText', 'minWeight', 'limit',
                         'offset', 'features', 'filter']
