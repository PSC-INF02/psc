from abstracter.workers.workers_settings import *
from abstracter.workers.compute_worker import *

class ActivateWorker(Worker):
    """
    Worker which activates a node in the concepts network.
    @see abstracter.concepts_network.ConceptNetwork
    """

    def __init__(self, target_id, activation_to_add,urgency=ACTIVATE_URGENCY):
        super(ActivateWorker, self).__init__(urgency)
        self.target_id = target_id
        self.activation_to_add = activation_to_add


    def run(self, context):
        """
        The Activate worker generates new Compute workers for every linked node
        It pushes a writeConcept worker if the node is activated enough.

        @param context The current context.
        @see abstracter.workers.compute_worker.ComputeWorker
        @see abstracter.Context
        """
        context.network[self.target_id]['a'] += self.activation_to_add
        if context.network[self.target_id]['a'] > ACTIVATION_ENABLING_CONCEPT_INSTANTIATION:
            pass
            #context.workers.push(WriteConceptWorker(self.target_id))
        for arc in context.network.out_arcs(self.target_id):
            context.workersManager.push(ComputeWorker(arc[1],urgency=arc[3]['w']))
        #for n in context.network.successors(self.target_id):
        #    context.workersManager.push(ComputeWorker(n))
        return ACTIVATE_DELTA_TIME


    def __str__(self):
        return "Activation of concept " + self.target_id + \
            " by " + self.activation_to_add.__str__()
