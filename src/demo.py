from abstracter.grammar.systran_parser import parse_systran
from abstracter.grammar.anaphora_resolution import demo

sents = parse_systran("../systran/3.clean.wsd.linear")


demo(sents)
