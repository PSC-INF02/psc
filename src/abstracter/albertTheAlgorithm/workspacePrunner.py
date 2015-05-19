"""
@file workspacePrunner.py

@brief THE algorithm
"""

# from math import exp


class workspacePrunner:

    def __init__(self, workspace, concept_network):
        self.wks = workspace
        self.cnetwork = concept_network

    def push_activation(self):
        for n, d in self.wks.items():
            if (d.__class__.__name__ != 'WordGroup' and
                    d['norm'] in self.cnetwork):
                self.cnetwork.activate([d['norm']], act=60)
                for k in self.wks.network.out_arcs(n):
                    self.cnetwork[d['norm']]['ic'] = (
                        int(100 - (100 - self.cnetwork[d['norm']]['ic']) / 1.5)
                    )

    def propagate(self, propagation_range=1):
        for i in range(propagation_range):
            self.cnetwork.propagate()

    def prune(self, prune_level=1):
        to_keep = [
            i for i in self.cnetwork.get_activated_nodes(offset=prune_level+1)
        ]
        items = [i for i in self.wks.items()]
        for n, d in items:
            if d['norm'] not in to_keep:
                self.wks.network.remove_node(n)
