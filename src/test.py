from abstracter.concepts_network import *

cn = ConceptNetwork()

cn.load("rc4")

cn.activate(["wayne_rooney", "steven_gerrard"])
for i in range(4):
    cn.propagate()
cn.print_activated_nodes(9)
