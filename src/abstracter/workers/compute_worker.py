from abstracter.workers.workers_settings import *
from abstracter.workers import *

class ComputeWorker(Worker):
    """
    Workers which compute the activation of a node in the concepts network.
    @see abstracter.concepts_network.ConceptNetwork
    """

    def __init__(self, target_id,urgency=COMPUTE_URGENCY):
        """
        @param target_id Id of the node to activate (a node in the conceptnetwork) (str).
        @param urgency Urgency of the worker, to be set manually if needed (integer).
        """
        super(ComputeWorker, self).__init__(urgency)
        self.target_id = target_id

    def run(self, context):
        """
        Computes node's activation.
        Then pushes new abstracter.workers.compute_worker.ComputeWorker workers 
        for each neighbour node in the workspace.

        @param context A Context object.
        """
        context.network.compute_activation(self.target_id)
        for arc in context.network.out_arcs(self.target_id):
            context.workersManager.push(ComputeWorker(arc[1],urgency=arc[3]['w']))
        return(COMPUTE_DELTA_TIME)

    def __str__(self):
        return "Calculating act of concept " + self.target_id
