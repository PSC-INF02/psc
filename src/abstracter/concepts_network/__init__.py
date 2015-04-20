from abstracter.util.json_stream import read_json_stream, JSONStreamWriter
from abstracter.util.network import Network
from math import log


class ConceptNetwork(Network):
    """
    @class ConceptNetwork
    @brief Class representing our Conceptnetwork.

    The ConceptNetwork is constructed as an extension of Network.
    We are free to change Network's implementation, since ConceptNetwork
    does not refer to any other python package.
    """

    def __init__(self):
        super(ConceptNetwork, self).__init__()

    def add_node(self, id, a, ic):
        """
        Adding a node with parameters concerning the concept network.

        @param id Node id (str).
        @param a Node activation.
        @param ic Node ic (importance conceptuelle).
        """
        super(ConceptNetwork, self).add_node(id=id, a=a, ic=ic)

    def add_edge(self, fromId, toId, w, r, key=0):
        """
        Adding an edge with parameters concerning the concept network.

        @param w Weight
        @param r Relation
        """
        if not self.has_node(fromId):
            self.add_node(id=fromId, a=0, ic=0)
        if not self.has_node(toId):
            self.add_node(id=toId, a=0, ic=0)
        if self.network.has_edge(fromId, toId, key):
            key += 1
        super(ConceptNetwork, self).add_edge(fromId=fromId, toId=toId, key=key, w=w, r=r)

    def shortest_path(self, fromId, toId):
        """
        Computes the shortest path between two nodes.
        """
        return super(ConceptNetwork, self).shortest_path(source=fromId, target=toId, weight=None)

    def compute_activation(self, id):
        """
        @brief Computes the new node activation.

        Computes the new node activation,  using :
        * a logarithmic divisor (depends on the connexity)
        * its neighbours' activation
        * its self-desactivation
        """
        # divlog = log(3 + len(self.inArcs(id))) / log(3)
        divlog = 1  # deactivated for now
        i = 0
        for arc in self.in_arcs(id):
            i = i + (arc[3]['w'] or 0) * self[arc[0]]['a']
        act = self[id]['a']
        i = i / (100 * divlog)  # neighbours
        d = act * (100 - (self[id]['ic'] or 100)) / 100  # self desactivation
        self[id]['a'] = int(min(act + i - d, 100))
        # we do not go beyond 100,  and activation is an integer

    def activate(self, id_list, act=60):
        for id in id_list:
            self[id]['a'] += act

    def propagate(self):
        """
        Compute the activation of all already activated nodes
        and their neighbours.
        """
        to_deactivate = list()
        # get all neighbours
        neighbours = dict()
        for n, d in self.nodes():
            if d['a'] > 0:
                to_deactivate.append(n)
                neighbours[n] = 0
                for arc in self.out_arcs(n):
                    neighbours[arc[1]] = 0
        # compute activation for all neighbours
        for n in neighbours:
            divlog = 1
            i = 0
            for arc in self.in_arcs(n):
                i = i + (arc[3]['w'] or 0) * self[arc[0]]['a']
            i = i / (100 * divlog)
            neighbours[n] = int(min(self[n]['a'] + i, 100))
        # change activation
        for n in neighbours:
            self[n]['a'] = neighbours[n]
        # deactivate
        for n in to_deactivate:
            self[n]['a'] = int(self[n]['a'] * (self[n]['ic'] or 100) / 100) # int(min(self[n]['a'] * (100 - (self[id]['ic'] or 100)) / 100))

    def print_activated_nodes(self, offset=0):
        for n, d in self.nodes():
            if d['a'] > offset:
                print(n + " : " + d['a'].__str__())

    ###########################################

    def load_nodes_from_stream(self, filename):
        """
        Load nodes from a .jsons file and insert them in the ConceptNetwork.
        """
        self.add_nodes_from(read_json_stream(filename))

    def load_edges_from_stream(self, filename):
        """
        Load edges from a .jsons file and insert them in the ConceptNetwork.
        """
        self.add_edges_from(read_json_stream(filename))

    def load_from_JSON_stream(self, nodes_files, edges_files):
        """
        @brief Loading from multiple jsons files.

        We load from a bunch of files, assuming that
        they contain node and edge data.
        This function has been unused, since we used only one file.
        """
        for f in nodes_files:
            self.load_nodes_from_stream(f)
        for f in edges_files:
            self.load_edges_from_stream(f)

    def save_to_JSON_stream(self, filenamebase):
        """
        Saves the network, creating two files :
        * "..._nodes.jsons"
        * "..._edges.jsons"
        Those files are encoded in JSONStream format.

        @param filenamebase Name of the ConceptNetwork.
        @see util.json_stream
        """
        nodes_writer = JSONStreamWriter(filenamebase + "_nodes.jsons")
        for n in self.nodes(data=True):
            nodes_writer.write(n)
        nodes_writer.close()
        edges_writer = JSONStreamWriter(filenamebase + "_edges.jsons")
        for e in self.edges(data=True):
            edges_writer.write(e)
        edges_writer.close()

    def load(self, arg, directory=""):
        """
        Small util to load a network directory.
        We store a ConceptNetwork object of name "rc" in a directory
        named "rc", with two files : "rc_nodes.jsons" and "rc_edges.jsons".

        @param arg Name of the ConceptNetwork
        @param directory May be "" (current directory) or "../", for example.
        """
        self.add_nodes_from(read_json_stream(directory + arg + "/" + arg + "_nodes.jsons"))
        self.add_edges_from(read_json_stream(directory + arg + "/" + arg + "_edges.jsons"))


if __name__ == '__main__':
    def _test():
        n = ConceptNetwork()
        n.add_node(id="toto", a=70, ic=5)
        n.add_node(id="babar", a=0, ic=6)
        n.add_edge(fromId="toto", toId="babar", r="haha", w=50)
        n.add_edge("toto", "babar", r="hihi", w=10.261645654)
        print(n["toto"])
        print(n.get_edge("toto", "babar", 0))
        print(n.get_edge("toto", "babar", 1))
        for v in n.outArcs("toto"):
            print(v)
            print(v[3]["w"])
        print(n["toto"]['a'])
        n.compute_activation("babar")
        print(n["babar"]["a"])
        n.remove_edge("toto", "babar", all=False, key=1)

    _test()
    pass
