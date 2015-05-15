#!/usr/bin/env python3

import abstracter.adapter.jsontree2workspace as j2w
import abstracter.workspace.workspace as workspace
import json
import abstracter.grammar.grammartree as gt
import abstracter.albertTheAlgorithm.workspacePrunner as wksP
import abstracter.concepts_network

wks = workspace.Workspace()

with open("../../fichiers_parses/0.grammartree.json") as jfile:
    piloup = json.load(jfile, cls=gt.GrammarTreeDecoder)

blah = j2w.jsonTree2W(wks)
blah.parse_forest([], piloup, piloup)

cn = abstracter.concepts_network.ConceptNetwork()
cn.load("rc5")

wp = wksP.workspacePrunner(wks, cn)
wp.push_activation()
wp.propagate(10)
wp.prune(299999999999999999)
print([i[1]['norm'] for i in wks.items()])
