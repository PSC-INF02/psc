from abstracter import Context
from abstracter.concepts_network import *

n=ConceptNetwork()
n.load_from_JSON_stream(nodes_files=["rc/rc_nodes.jsons"],edges_files=["rc/rc_edges.jsons"])

c=Context(n)
c.activate("jim_smith",60)
c.run(5)

def print_activated_nodes(network):
	for n,d in network.nodes():
		if d['a'] > 0:
			print(n+" : "+d['a'].__str__())


print_activated_nodes(n)