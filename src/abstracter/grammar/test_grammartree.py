import sys
import json
from abstracter.grammar import systran_to_grammartree
from abstracter.grammar.grammartree import GrammarTreeEncoder

if __name__ == "__main__":
    tree = systran_to_grammartree(sys.argv[1])
    print(json.dumps(tree, cls=GrammarTreeEncoder))
