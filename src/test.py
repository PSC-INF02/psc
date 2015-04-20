from abstracter.concepts_network import *

cn = ConceptNetwork()

cn.load("rc4")

cn.activate(["wayne_rooney", "steven_gerrard"])
cn.propagate()
cn.propagate()
cn.print_activated_nodes(20)
