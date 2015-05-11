import json
from abstracter.grammar.systran_parser import parse_systran, to_grammar_tree
from abstracter.grammar.grammartree import GrammarTreeEncoder
from abstracter.grammar.group_grammartree import group_grammartree

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = parse_systran(file)
    tree = to_grammar_tree(data)

    group_grammartree(tree)

    print(json.dumps(tree, cls=GrammarTreeEncoder))
