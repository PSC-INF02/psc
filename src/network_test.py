from abstracter import Context
from abstracter.concepts_network import *
from abstracter.parsers import retriever as ret

n = ConceptNetwork()
n.load_from_JSON_stream(nodes_files=["rc3/rc3_nodes.jsons"],edges_files=["rc3/rc3_edges.jsons"])
c = Context(n)

######
## test 1
######

c.activate("wayne_rooney", 60)
c.run(10)


def print_activated_nodes(network):
    for n, d in network.nodes():
        if d['a'] > 0:
            print(n + " : " + d['a'].__str__())


print_activated_nodes(n)


####
##test 2
###

#text="Wayne Rooney was in a bad mood yesterday because I don't know yet."
#doublelist=ret.retrieve_words_names(text)
#print(doublelist)
#for w in doublelist[0]:
#    c.activate(w.replace(" ","_"),30)
#for w in doublelist[1]:
#    c.activate(w.replace(" ","_"),50)
#c.run(10)
#print_activated_nodes(n)
