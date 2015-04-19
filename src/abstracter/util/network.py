"""@file network.py
@brief Interface with the networkx package.

"""

import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import json


class Network:
    """
    @class Network
    Class representing a network.
    It uses the package networkx.
    """
    def __init__(self):
        self.network = nx.MultiDiGraph()

    def __getitem__(self, id):
        try:
            return self.network.node[id]
        except KeyError:
            return None

    def get_node(self, id):
        return self.network.node[id]

    def add_node(self, id, **kwargs):
        self.network.add_node(id)
        for akey, avalue in kwargs.items():
            self[id][akey] = avalue

    def add_edge(self, fromId, toId, key=0, **kwargs):
        """
        Add an edge with as many data as you want.
        Of course, it's supposed to contain a weight and a relation,
        but we can deal without (no weight is treated like a weight 0)
        """
        self.network.add_edge(fromId, toId, key)
        for akey, avalue in kwargs.items():
            self.network[fromId][toId][key][akey] = avalue

    def remove_node(self, id):
        self.network.remove_node(id)

    def remove_edge(self, fromId, toId, key=None, all=True):
        if all:
            while self.has_edge(fromId, toId):
                self.network.remove_edge(fromId, toId)
        else:
            if self.has_edge(fromId, toId, key):
                self.network.remove_edge(fromId, toId, key)

    def has_node(self, id):
        return self.network.has_node(id)

    def has_edge(self, fromId, toId, key=None):
        return self.network.has_edge(fromId, toId, key)

    def predecessors(self, id):
        return self.network.predecessors_iter(id)

    def successors(self, id):
        return self.network.successors_iter(id)

    def get_edge(self, fromId, toId, key=0):
        return self.network[fromId][toId][key]

    def out_arcs(self, id):
        return self.network.out_edges_iter(id, data=True, keys=True)

    def in_arcs(self, id):
        return self.network.in_edges_iter(id, data=True, keys=True)

    def nodes(self, data=True):
        return self.network.nodes(data)

    def edges(self, data=True):
        return self.network.edges(data=data)

    def shortest_path(self, source=None, target=None, weight=None):
        return nx.shortest_path(self.network, source=source, target=target, weight=weight)

    def add_nodes_from(self, it):
        self.network.add_nodes_from(it)

    def add_edges_from(self, it):
        self.network.add_edges_from(it)

    ###########################################################
    # JSON generating and decoding
    ##############################################

    def save_to_JSON(self, filename="temp.json"):
        with open(filename, 'w') as file:
            json.dump(json_graph.node_link_data(self.network), file)

    def load_from_JSON(self, filename="temp.json"):
        with open(filename, 'r') as file:
            self.network = json_graph.node_link_graph(json.load(file))

    def draw(self, filename=None):
        pos = nx.spring_layout(self.network, dim=2, weight='w', scale=1)
        nx.draw_networkx_nodes(self.network, pos=pos, font_family='sans-serif')
        nx.draw_networkx_edges(self.network, pos=pos, font_family='sans-serif')
        nx.draw_networkx_labels(self.network, pos=pos, font_family='sans-serif')
        # nx.draw_networkx_edge_labels(self.network, pos=pos, font_family='sans-serif')
        if filename:
            plt.savefig(filename)
        plt.show()

    def pretty_draw(self, filename=None,
                    node_size=3500, node_color='blue', node_alpha=0.3,
                    node_text_size=12,
                    edge_color='blue', edge_alpha=0.3, edge_tickness=1,
                    edge_text_pos=0.4,
                    text_font='sans-serif'):
        """
        Pretty drawing, for very small networks only.
        """
        graph_pos = nx.spring_layout(self.network, k=0.2, iterations=40)
        nx.draw_networkx_nodes(self.network, graph_pos, node_size=node_size,
                               alpha=node_alpha, node_color=node_color)
        nx.draw_networkx_edges(self.network, graph_pos, width=edge_tickness,
                               alpha=edge_alpha, edge_color=edge_color)
        nx.draw_networkx_labels(self.network, graph_pos, font_size=node_text_size,
                                font_family=text_font)
        labels = {}
        for e in self.edges():
            labels[e] = self.get_edge(e[0], e[1])['r']
        nx.draw_networkx_edge_labels(self.network, graph_pos, edge_labels=labels,
                                     label_pos=edge_text_pos)
        plt.show()
