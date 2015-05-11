from abstracter.grammar.systran_parser import parse_systran, to_grammar_tree
from abstracter.grammar.group_grammartree import group_grammartree

def systran_to_grammartree(file):
    data = parse_systran(file)
    tree = to_grammar_tree(data)
    group_grammartree(tree)
    return tree
