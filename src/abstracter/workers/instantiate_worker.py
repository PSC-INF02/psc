from abstracter.workers.workers_settings import *
from abstracter.workers import *

class InstantiateWorker(Worker):
    """
    Workers which Instantiates a node in the workspace.
    @see abstracter.workspace.Workspace
    """

    def __init__(self, target_id,urgency=INSTANTIATE_URGENCY):
        """
        @param target_id Id of the target (str).
        @param urgency Urgency of the worker, to be set manually if needed (integer).
        """
        super(ComputeWorker, self).__init__(urgency)
        self.target_id = target_id

    def run(self, context):
        """
        @param context A Context object.
        """
        context.workspace.add_node(self.target_id)
        pass

    def __str__(self):
        return "Instantiating concept " + self.target_id
