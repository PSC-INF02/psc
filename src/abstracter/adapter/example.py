#!/usr/bin/env python3

import abstracter.adapter.jsontree2workspace as j2w
import abstracter.workspace.workspace as workspace
import json
import abstracter.grammar.grammartree as gt

wks = workspace.Workspace()

with open("../../fichiers_parses/0.grammartree.json") as jfile:
    piloup = json.load(jfile, cls=gt.GrammarTreeDecoder)

blah = j2w.jsonTree2W(wks)
blah.parse_forest([], piloup.children, piloup)
