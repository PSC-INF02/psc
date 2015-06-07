"""
@file cn_info.py

@brief Give and print information on a ConceptNetwork.

The information is only printed, but it can be interfaced
with matplotlib to obtains immediately graphics.

Example :
@code
cn = ConceptNetwork()
cn.load("rc4")

print_much_out_arcs(cn)
draw_a_connected_component(cn, 2)
connected_components_sizes(cn)
out_edges(cn)
in_edges(cn)
@endcode

"""

from abstracter.concepts_network import ConceptNetwork


def print_much_out_arcs(cn):
    """
    Print nodes which have much out edges, and how
    many they have.
    """
    for n, d in cn.nodes():
        toto = len(list(cn.out_arcs(n)))
        if toto > 60:
            print(n + " : " + toto.__str__())


def draw_a_connected_component(cn, size_wanted):
    """
    Search for connected components and draw one.
    """
    x = []
    for c in net.weakly_connected_component_subgraphs(cn.network):
        x.append(len(c))
        if len(c) == size_wanted: # or what we want
            cn2 = ConceptNetwork()
            for n, d in c.nodes(data=True):
                cn2.add_node(n, a=0, ic=0)
            for e in c.edges(data=True):
                cn2.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])
            cn2.pretty_draw()
            return


def connected_components_sizes(cn):
    """
    How many components for each size.
    For example, there may be many components of size 2,
    (two words with an "antonym" edge).
    """
    x = []
    for c in net.weakly_connected_component_subgraphs(cn.network):
        x.append(len(c))    
    y = {}

    for c in x:
        if c in y:
            y[c] += 1
        else:
            y[c] = 1
    print(y)


def out_edges(cn):
    """
    How many nodes for each number of out_edges.
    """
    result = dict()
    for n, d in cn.nodes():
        toto = len(list(cn.out_arcs(n)))
        if toto in result:
            result[toto] += 1
        else:
            result[toto] = 1
    print(result)


def in_edges(cn):
    """
    How many nodes for each number of in_edges.
    """
    result = dict()
    for n, d in cn.nodes():
        toto = len(list(cn.in_arcs(n)))
        if toto in result:
            result[toto] += 1
        else:
            result[toto] = 1
    print(result)
