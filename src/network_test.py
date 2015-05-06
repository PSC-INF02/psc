from abstracter.concepts_network import ConceptNetwork

cn = ConceptNetwork()

cn.load("rc4")

for n, d in cn.nodes():
    toto = len(list(cn.in_arcs(n)))
    if toto > 500:
        print(n + " : " + toto.__str__())
