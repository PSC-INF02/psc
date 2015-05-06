from abstracter.grammar.systran_parser import parse_systran
from abstracter.grammar.anaphora_resolution import demo
from abstracter.grammar.systran_parser import parse_systran
from abstracter.grammar.verb_groups import get_verb_groups, print_verb_groups

sents = parse_systran("../systran/3.clean.wsd.linear")
nps = get_verb_groups(sents)
print(nps)
print_verb_groups(sents)

#sents = parse_systran("../systran/3.clean.wsd.linear")


#demo(sents)
