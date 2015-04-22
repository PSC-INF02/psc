import json
from abstracter.grammar.systran_parser import parse_systran, to_grammar_tree
from abstracter.grammar.grammartree import GrammarTreeEncoder, GrammarTreeDecoder, group_grammar_tree

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = parse_systran(file)
    tree = to_grammar_tree(data)

    group_grammar_tree(tree)

    # tree = json.loads(json.dumps(tree, cls=GrammarTreeEncoder), cls=GrammarTreeDecoder)
    print(json.dumps(tree, cls=GrammarTreeEncoder))
