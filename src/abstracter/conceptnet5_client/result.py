"""@file result.py
Methods for parsing a query result.

@see data_settings.py Settings used.
"""
import ast
import abstracter.conceptnet5_client.data_settings as data_settings


##############################
# These are the primary keys returned by a query (in raw json data).
# @param numFound : Number of edges found.\n
# @param edges : Edges found (only in LookUp and Search).\n
# @param similar : Only in Association.
################################

SUPPORTED_KEYS = ['numFound', 'maxScore', 'edges', 'terms', 'similar']


def rel_to_word(relation='/r/HasA'):
    """
    Small util to transform a relation into a word : '/r/HasA' becomes HasA.
    """
    return relation.split('/')[2]


def concept_to_word(concept='/c/en/dog'):
    """
    Small util to transform a concept into a word : '/c/en/dog' becomes dog.
    """
    return concept.split('/')[3]


def is_relevant_concept(word):
    """
    Check if the concept is relevant, that is,
    if it doesn't have too much undescores (some concepts
    in Conceptnet5 are more like complete sentences and they
    are not likely to be found again in a text).
    """
    return len(word.split('_')) < data_settings.MAX_UNDERSCORES_ALLOWED + 2


def parse_similar_concepts(json_data):
    """
    Transforms [['/c/en/dog',0.995654654]] into ['dog',0.995]

    @param json_data Query result encoded in JSON.
    """
    return list([concept_to_word(w[0]), int(w[1] * 1000) / 1000] for w in json_data["similar"])


def parse_relevant_edges(json_data, clean_self_ref=True):
    """
    Transforms edges of a query result into result.Edge objects.

    Only relevant edges are kept (relevant relations)
    When the result.Edge object is created, only relevant attributes are kept.
    @see data_settings.RELEVANT_EDGES_ATTRIBUTES
    @see data_settings.USEFUL_CONCEPTNET_EDGES

    @param json_data Query result encoded in JSON.
    @param clean_self_ref Indicates if edges that have the same
    start and end have to be dismissed.
    """
    edges = []
    if 'edges' not in json_data:
        return edges
    for edge_str in json_data['edges']:
        e = Edge(edge_str)
        if e.rel in data_settings.USEFUL_CONCEPTNET_EDGES:
            # and e.weight*USEFUL_CONCEPTNET_EDGES[e.rel] > MINIMUM_WEIGHT_ALLOWED: unuseful
            e.rel = rel_to_word(e.rel)
            e.start = concept_to_word(e.start)
            e.end = concept_to_word(e.end)
            if is_relevant_concept(e.start) and is_relevant_concept(e.end):
                if clean_self_ref:
                    if e.start != e.end:
                        edges.append(e)
                else:
                    edges.append(e)
    return edges


class Edge(object):
    '''
    @class Edge
    This class implements the methods for representing an edge
    in Conceptnet5 and manipulating it.
    '''

    def __init__(self, edge_str):
        edge_dict = ast.literal_eval(str(edge_str))
        for attribute in data_settings.RELEVANT_EDGES_ATTRIBUTES:
            self.__dict__[attribute] = (edge_dict[attribute])

    def print_assertion(self):
        '''
        Prints the lemmas of this edge with start, rel, end lemmas.
        @warning unused
        '''
        print('%s %s %s' % (self.start_lemmas, self.rel, self.end_lemmas))

    def print_edge(self):
        '''
        Prints the normalized edge data with start node, rel, end node.
        '''
        print('(%s -> %s -> %s , %d)' % (self.start, self.rel, self.end, self.weight))

    def print_all_attrs(self):
        '''
        Prints all attributes regarding to this edge.
        @warning unused
        '''
        attrs = vars(self)
        print('\n'.join('%s: %s' % item for item in attrs.items()))
