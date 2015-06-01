from abstracter.concepts_network import *
import os

if not os.path.isdir("drawing_test/"):
    os.mkdir("drawing_test/")

cn = ConceptNetwork()

cn.load("rc4")

NETWORK = ConceptNetwork()

# # cn.activate(["wayne_rooney", "steven_gerrard"])
# cn.activate(["wayne_rooney", "manchester_united_f.c."])
# for i in range(3):
#     cn.propagate()
#     cn.print_activated_arcs(10)
#     print()
# # cn.print_activated_arcs(9)


def num_activated_nodes(net, offset):
    k = 0
    for n, d in net.nodes():
        if d['a'] > offset:
            k += 1
    return k


#cn.activate(["wayne_rooney", "manchester_united_f.c."], 60)
cn.activate(["water"], 60)
for i in range(10):
    NETWORK = ConceptNetwork()
    #cn.print_activated_arcs(10)
    print("Étape " + i.__str__() + " : " + num_activated_nodes(cn, 10).__str__())
    #print()
    for n in cn.get_activated_nodes(10):
        NETWORK.add_node(n, ic=cn[n]['ic'], a=cn[n]['a'])
    for e in cn.get_activated_arcs(10):
        #print(e)
        NETWORK.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])
    #for n in NETWORK.edges():
    #    print(n)
    #print()
    NETWORK.pretty_draw("drawing_test/" + i.__str__())
    cn.propagate()



#################"test2"

# result = dict()
# for n, d in cn.nodes():
#     toto = len(list(cn.out_arcs(n)))
#     #if(len(list(cn.in_arcs(n))) == 0 and n != ""):
#     #    print(n)
#     #    assert 0 == 1
#     if toto in result:
#         result[toto] += 1
#     else:
#         result[toto] = 1

# res = 0
# tot = 0
# #for n in result:
# #    print(n.__str__() + " " + result[n].__str__())

# for n in result:
#     tot += result[n]
#     res += n * result[n]
# print(res / tot)


#################""test3

# result = dict()
# for n, d in cn.nodes():
#     ic = d["ic"]
#     ic = int(ic / 10) * 10
#     if ic in result:
#         result[ic] = result[ic][0] + 1, result[ic][1] + len(list(cn.in_arcs(n)))
#     else:
#         result[ic] = 1, len(list(cn.in_arcs(n)))

# for n in result:
#     print(n.__str__() + " " + (result[n][1] / result[n][0]).__str__())
