try:
    from concepts_network import *
    from workers.activate_worker import *
except ImportError:
    from abstracter.concepts_network import *
    from abstracter.workers.activate_worker import *
    from abstracter.workspace import *



class Context:
    """
    General context in which we work.
    It contains a workersmanager, a concepts network, a workspace and maybe other objects.
    """
    
    
    def __init__(self,network=None):
        self.workersManager=WorkersManager(self)
        if network:
            self.network=network
        else:
            self.network=ConceptNetwork()
            self.load_network()
        self.workspace=Workspace(self)

    def load_network(self,name="rc"):
        self.network.load(name)

    def test(self):
        self.network.add_node(id="babar",ic=2,a=0)
        self.network.add_edge(fromId="toto",toId="babar",w=20,r="nothing in common")
        self.network.add_edge(fromId="toto",toId="elephant",w=100,r="useless")
        print(self.network["toto"])
        self.workersManager.push(ActivateWorker("toto",60))
        self.run(10)
        print(self.network["babar"]["a"])

    def activate(self,node,activation):
        self.workersManager.push(ActivateWorker(node,activation))

    def print_activated_nodes(self):
        for n,d in self.network.nodes():
            if d['a'] > 0:
                print(n+" : "+d['a'].__str__())

    def get_activated_nodes(self):
        for n,d in self.network.nodes():
            if d['a'] > 0:
                yield n,d


    def run(self,max_time):
        print("Running for "+max_time.__str__()+" time.")
        while self.workersManager.time<max_time and not self.workersManager.isEmpty():
            #print(self.workersManager)
            #self.print_activated_nodes()
            self.workersManager.runWorker()
        #print(self.workersManager)

if __name__=="__main__":
	c=Context()
	c.test()




