from abstracter.util.network import *


class OldWorkspace(Network):
    """
    The workspace is supposed to be smaller than the concept network.
    It is also stored as a network object, using networkx.
    """

    def __init__(self,context):
        self.context=context

    def add_node(self,id):
        """
        Adding a node with parameters concerning the workspace.
        """
        super(Workspace,self).add_node(id=id)

    def add_edge(self,fromId,toId,w,r,key=0):
        """
        Adding an edge with parameters concerning the concept network.
        @param w Weight
        @param r Relation
        """
        if not self.network.has_node(fromId):
            self.add_node(id=fromId,a=0,ic=0)
        if not self.network.has_node(toId):
            self.add_node(id=toId,a=0,ic=0)
        if self.network.has_edge(fromId,toId,key):
            key=key+1
        super(Workspace,self).add_edge(fromId=fromId,toId=toId,key=key,w=w,r=r)

##TODO : OTHER METHODS

