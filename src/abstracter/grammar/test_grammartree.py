import json
from abstracter.grammar.systran_parser import parse_systran, to_grammar_tree
from abstracter.grammar.grammartree import GrammarTreeEncoder, group_grammar_tree

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    data = parse_systran(file)
    tree = to_grammar_tree(data)

    group_grammar_tree(tree)

    # Make relations human-readable
    for w in tree.leaves():
        for tag, path in w.relation_tags():
            w['tags'][tag] = ", ".join(map(str, path)) + ": " + tree[path]['text']
        w['relations'] = [", ".join(map(str, path)) + ": " + tree[path]['text'] for path in w['relations']]

    print(json.dumps(tree, cls=GrammarTreeEncoder))
