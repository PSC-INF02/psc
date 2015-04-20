from abstracter.workspace.workspace import * 
from abstracter.util.systran_parser import parse_systran
from abstracter.adapter.json2workspace import Json2W

parsedText = parse_systran("11.clean.wsd.linear")
wks = Workspace()
jsn = Json2W(wks)
jsn.parse(parsedText)
