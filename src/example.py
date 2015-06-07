#!/usr/bin/env python3

import abstracter.adapter.jsonTreeToWorkspace as j2w
import abstracter.workspace.workspace as workspace
import json
import abstracter.grammar.grammartree as gt
import abstracter.albertTheAlgorithm.workspacePrunner as wksP
import abstracter.concepts_network

wks = workspace.Workspace()

with open("0.grammartree.json") as jfile:
    piloup = json.load(jfile, cls=gt.GrammarTreeDecoder)

blah = j2w.JSONTreeToWorkspace(wks)
blah.parse_forest([], piloup, piloup)

cn = abstracter.concepts_network.ConceptNetwork()
cn.load("rc5")

#print([i[1]['norm'] for i in wks.items()])
wp = wksP.WorkspacePrunner(wks, cn)
wp.push_activation()
wp.propagate(3)
wp.prune(60)
print([i[1]['norm'] for i in wks.items()])
