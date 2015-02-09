from abstracter.workers.workers_settings import *
from abstracter.workers import *

class ComputeWorker(Worker):
    """
    Workers which compute nodes' activation.
    """

    def __init__(self, target_id,urgency=COMPUTE_URGENCY):
        """
        :param target_id: id of the node to activate (a node in the conceptnetwork)
        :type target_id: str
        :param urgency: Urgency of the worker, to be set manually if needed
        :type urgency: integer
        """
        super(ComputeWorker, self).__init__(urgency)
        self.target_id = target_id

    def run(self, context):
        """
        Computes node's activation.
        Then pushes new compute workers for each neighbour node in the workspace.
        """
        context.network.compute_activation(self.target_id)
        for arc in context.network.out_arcs(self.target_id):
            context.workersManager.push(ComputeWorker(arc[1],urgency=arc[3]['w']))
        return(COMPUTE_DELTA_TIME)

    def __str__(self):
        return "Calculating act of concept " + self.target_id
