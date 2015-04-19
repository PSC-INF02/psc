
from abstracter.workspace import *
from abstracter.util import *
from abstracter.adapter import Json2W

parsedText = parse_systran("11.clean.wsd.liner")
wks = workspace.Workspace()
jsn = adapter.Json2W(workspace)
jsn.parse(parsedText)
