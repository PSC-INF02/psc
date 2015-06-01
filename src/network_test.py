from abstracter.concepts_network import ConceptNetwork
import networkx as net

cn = ConceptNetwork()

cn.load("rc5")

# for n, d in cn.nodes():
#     toto = len(list(cn.in_arcs(n)))
#     if toto > 500:
#         print(n + " : " + toto.__str__())

import matplotlib.pyplot as plot
#x = [len(c) for c in net.connected_component_subgraphs(cn.network)]

x = []

for c in net.weakly_connected_component_subgraphs(cn.network):
    x.append(len(c))
    if len(c) == 16 or len(c) == 5:
        cn2 = ConceptNetwork()
        for n, d in c.nodes(data=True):
            cn2.add_node(n, a=0, ic=0)
        for e in c.edges(data=True):
            cn2.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])
        cn2.pretty_draw()

y = {}

for c in x:
    if c in y:
        y[c] += 1
    else:
        y[c] = 1

print(y)

#{16: 1, 2: 83, 3: 43, 4: 19, 5: 1, 6: 5, 9: 2, 26825: 1, 18: 1}
#{16: 1, 1: 1300, 2: 83, 3: 43, 4: 19, 5: 1, 6: 5, 9: 2, 26825: 1, 18: 1}

#x = [len(c) for c in net.weakly_connected_component_subgraphs(cn.network)]

#y = [c for c in x if c > 10]
#print(len(x))
#print(len(y))
#print(y)
#plot.hist(x, 10, histtype='bar',)
#plot.show()

#1456
#3
#[26825, 18, 16]
#
#


