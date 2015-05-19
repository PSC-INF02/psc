#!/usr/bin/env python3

import abstracter.adapter.jsontree2workspace as j2w
import abstracter.workspace.workspace as workspace
import json
import abstracter.grammar.grammartree as gt
import abstracter.albertTheAlgorithm.workspacePrunner as wksP
import abstracter.concepts_network
import abstracter.util.network as network


def srt(x):
    a, b = x
    return b

wks = workspace.Workspace()

with open("../../fichiers_parses/thephrase.json") as jfile:
    piloup = json.load(jfile, cls=gt.GrammarTreeDecoder)

blah = j2w.jsonTree2W(wks)
blah.parse_forest([], piloup, piloup)

cn = abstracter.concepts_network.ConceptNetwork()
cn.load("rc5")

wp = wksP.workspacePrunner(wks, cn)
wp.push_activation()
wp.propagate(20)
print(
    sorted([(i[1]['norm'], cn[i[1]['norm']]['a'])
            for i in wks.items() if cn[i[1]['norm']] is not None], key=srt)
)
# wp.prune(199999999999999999)
# print([i[1]['norm'] for i in wks.items()])
nw = network.Network()
for node in wks.items():
    # if "syntagm" in node[1]:
    id = node[0]
    newid = node[1]["norm"]
    nw.add_node(newid, syntagm=node[1])

for edge in wks.network.edges():
    if "syntagm" in wks.network[edge[0]] and "syntagm" in wks.network[edge[1]]:
        from_node = wks.network[edge[0]]["syntagm"]["norm"]
        to_node = wks.network[edge[1]]["syntagm"]["norm"]
        nw.add_edge(from_node, to_node, **edge[2])

for edge in nw.out_arcs("he"):
    nw.add_edge("sepp_blatter", edge[1], **edge[3])
nw.remove_node("he")
for edge in nw.out_arcs("he"):
    nw.add_edge("sepp_blatter", edge[1], **edge[3])
nw.remove_node("sepp_blatter is the favourite "
               "to win a fifa race he vowed "
               "he would not stand for")
nw.pretty_draw()
