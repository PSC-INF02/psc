"""
@file workspacePrunner.py

@brief The main algorithm.
"""


class WorkspacePrunner:
    """
    @class WorkspacePrunner

    @brief Workspace prunner.

    Given a concepts_network.ConceptNetwork object and
    a workspace fulled with information,
    performs the selection of information within
    the workspace, using ConceptNetwork's activation.
    """

    def __init__(self, workspace, concept_network):
        self.wks = workspace
        self.cnetwork = concept_network

    def push_activation(self):
        """
        @warning The function performs a change in the ics of
        the workspace's items, which is not supposed to happen
        in theory (we had to do this in order to check
        the functionality of the algorithm).
        """
        for n, d in self.wks.items():
            if (d.__class__.__name__ != 'WordGroup' and
                    d['norm'] in self.cnetwork):
                self.cnetwork.activate([d['norm']], act=60)
                for k in self.wks.network.out_arcs(n):
                    self.cnetwork[d['norm']]['ic'] = (
                        int(100 - (100 - self.cnetwork[d['norm']]['ic']) / 1.5)
                    )

    def propagate(self, propagation_range=1):
        """
        Propagate activation in the ConceptNetwork.

        @param propagation_range How many times we have
        to perform the propagation.
        """
        for i in range(propagation_range):
            self.cnetwork.propagate()

    def prune(self, prune_level=1):
        """
        Remove from the workspace all nodes that are not activated enough
        in the ConceptNetwork.
        @todo There are plenty ways of performing this
        operation (the ConceptNetwork contains more information
        than pure activation).
        """
        to_keep = [
            i for i in self.cnetwork.get_activated_nodes(offset=prune_level + 1)
        ]
        items = [i for i in self.wks.items()]
        for n, d in items:
            if d['norm'] not in to_keep:
                self.wks.network.remove_node(n)
