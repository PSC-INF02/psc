import json
from abstracter.grammar.utils import *
from abstracter.util.unionfind import UnionFind

class GrammarTree:
    def __init__(self, children=[]):
        self.id = None
        self.parent = None
        self.root = self
        self.children = list(children)
        self.contents = {}

    def __getitem__(self, l):
        if isinstance(l, int):
            return self.children[l]
        elif isinstance(l, str):
            return self.contents[l]
        else:
            if len(l) == 0:
                return self
            elif len(l) == 1:
                return self[l[0]]
            else:
                tail = l[1:]
                if len(tail) == 1:
                    tail = tail[0]
                return self[l[0]][tail]

    def __setitem__(self, l, v):
        if isinstance(l, int):
            self.children[l] = v
        elif isinstance(l, str):
            self.contents[l] = v
        else:
            if len(l) == 0:
                raise IndexError()
            elif len(l) == 1:
                self[l[0]] = v
            else:
                tail = l[1:]
                if len(tail) == 1:
                    tail = tail[0]
                self[l[0]][tail] = v

    def __delitem__(self, l):
        if isinstance(l, int):
            del self.children[l]
        elif isinstance(l, str):
            del self.contents[l]
        else:
            if len(l) == 0:
                raise IndexError()
            elif len(l) == 1:
                del self[l[0]]
            else:
                tail = l[1:]
                if len(tail) == 1:
                    tail = tail[0]
                del self[l[0]][tail]

    def __contains__(self, l):
        if isinstance(l, int):
            return False
        elif isinstance(l, str):
            return l in self.contents
        else:
            if len(l) == 0:
                raise IndexError()
            elif len(l) == 1:
                return l[0] in self
            else:
                tail = l[1:]
                if len(tail) == 1:
                    tail = tail[0]
                return tail in self[l[0]]


    def __iter__(self):
        return iter(self.children)

    def nodes(self, depth=None, kind=None):
        if (depth is None or depth == 0) and (kind is None or ('kind' in self and self['kind'] == kind)):
            yield self

        if (depth is None or depth != 0):
            for c in self.children:
                if depth is None:
                    gen = c.nodes(kind=kind)
                else:
                    gen = c.nodes(depth=depth - 1, kind=kind)
                if gen is not None:
                    yield from gen


    def leaves(self):
        for c in self.children:
            if isinstance(c, GrammarTree):
                yield from c.leaves()
            else:
                yield c

    def add(self, subtree):
        subtree.id = len(self.children)
        subtree.parent = self
        self.children.append(subtree)
        for n in subtree.nodes():
            n.root = self.root

    def subpath(self, path):
        d = 0  # Depth in the root tree
        rpath = []
        root = self
        while root.parent is not None:
            d += 1
            rpath = [root.id] + rpath
            root = root.parent

        if rpath == path[:d]:
            return path[d:]
        else:
            raise IndexError("%s is not a path of tree %s" % (str(path), str(rpath)))


    def group_children(self, groups):
        """
        Groups the children according to a given equivalence relation.

        @param groups A list of groups of ids. Overlapping groups will be merged

        @return A map from the old node locations in the tree to their new one
        """

        # Construct the equivalence classes
        uf = UnionFind()
        for r in groups:
            uf.union(*r)

        if not set(uf) <= set(range(len(self.children))):
            raise IndexError("%s is not a subset of [0 .. %d]" % (str(list(uf)), len(self.children) - 1))

        # Compute the set of all singletons
        singletons = set(range(len(self.children)))
        for i in range(len(self.children)):
            j = uf[i]
            if i != j:
                singletons.discard(i)
                singletons.discard(j)

        # Map an id from each (non-singleton) equivalence class to a new empty tree
        group_map = {i:GrammarTree() for i in range(len(self.children)) if uf[i] == i and i not in singletons}
        new_groups = list(group_map.values())

        # Add each object to its group, and reconstruct the tree
        children = self.children
        self.children = []
        # added_groups = set()
        id_map = {}
        for i, o in enumerate(children):
            if i in singletons:
                self.add(o)
                id_map[i] = [o.id]

            else:
                parent_id = uf[i]
                group = group_map[parent_id]

                if group.id is None:
                    # added_groups.add(parent_id)
                    self.add(group)

                group.add(o)
                id_map[i] = [group.id, o.id]

        return id_map, new_groups

    def group_words(self, groups, kind=None):
        id_map, new_groups = self.group_children(groups)

        # Get the root and the path from root to self
        d = 0  # Depth in the root tree
        path = []
        root = self
        while root.parent is not None:
            d += 1
            path = [root.id] + path
            root = root.parent

        # Redirect tags to new ids
        for w in root.leaves():
            for tag, val in w['tags'].items():
                if is_relation_tag(tag) and val[:d] == path:
                    w['tags'][tag] = val[:d] + id_map[val[d]] + val[d + 1:]
            if 'relations' in w:
                w['relations'] = [r[:d] + id_map[r[d]] + r[d + 1:] for r in w['relations'] if r[:d] == path] + [r for r in w['relations'] if r[:d] != path]

        # Compute node name from descendants
        for x in self.children:
            if hasattr(x, 'children'):
                x['text'] = " ".join(y['text'] for y in x.children)

        if kind is not None:
            for g in new_groups:
                g['kind'] = kind

        return new_groups


class Word(GrammarTree):
    def __init__(self, w):
        self.contents = w
        self.id = w['id']


    def __getitem__(self, k):
        return self.contents[k]

    def __setitem__(self, k, v):
        self.contents[k] = v

    def __delitem__(self, k):
        del self.contents[k]

    def __iter__(self):
        raise TypeError("Cannot iterate over a word")

    def nodes(self, depth=None, kind=None):
        if (depth is None or depth == 0) and (kind is None or ('kind' in self and self['kind'] == kind)):
            yield self

    def leaves(self):
        yield self

    def add(self, subtree):
        pass

    def group_children(self, groups):
        pass

    def group_words(self, groups, kind=None):
        pass

    def relation_tags(self):
        for tag, path in self['tags'].items():
            if is_relation_tag(tag):
                yield (tag, path)



class GrammarTreeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GrammarTree):
            o = obj.contents.copy()
            if obj.id:
                o['id'] = obj.id

            # Make relations human-readable
            for tag, path in o.get('tags', {}).items():
                if is_relation_tag(tag):
                    o['tags'][tag] = ", ".join(map(str, path)) + ": " + obj.root[path]['text']

            if isinstance(obj, Word):
                o['relations'] = [", ".join(map(str, path)) + ": " + obj.root[path]['text'] for path in o['relations']]
            else:
                o['children'] = obj.children

            return o

        else:
            return json.JSONEncoder.default(self, obj)


class GrammarTreeDecoder(json.JSONDecoder):
    @staticmethod
    def object_to_tree(o):
        if 'children' in o:
            ret = GrammarTree()
            ret.children = [GrammarTreeDecoder.object_to_tree(x) for x in o['children']]
            del o['children']
            ret.contents = o
        else:
            ret = Word(o)
            ret['relations'] = [[int(x) for x in val.split(':')[0].split(', ')] for val in o['relations']]

        if 'tags' in ret:
            for tag, val in ret['tags'].items():
                if is_relation_tag(tag):
                    ret['tags'][tag] = [int(x) for x in val.split(':')[0].split(', ')]
                else:
                    ret['tags'][tag] = val

        if 'id' in ret:
            ret.id = ret['id']

        return ret

    def decode(self, s):
        tree = GrammarTreeDecoder.object_to_tree(super().decode(s))

        for n in tree.nodes():
            n.root = tree

        return tree



def group_grammar_tree(gtree):
    for paragraph in gtree:
        # Group any connected words into 'sentences'
        any_eq = []
        for w in paragraph.leaves():
            any_eq.append([paragraph.subpath(path)[0] for _, path in w.relation_tags()] + [w.id])
        paragraph.group_words(any_eq, kind='sentence')

    for sentence in gtree.nodes(depth=2, kind='sentence'):
        # # Use given 'relations' attribute
        # relations_eq = []
        # for w in sentence.leaves():
        #     relations_eq.append([sentence.subpath(rel)[0] for rel in w["relations"]])
        #     del w['relations']
        #
        # sentence.group_words(relations_eq, kind='group')

        # Group noun phrases
        noun_phrases_eq = []
        for g in sentence:
            gid = g.id
            eq = [gid]
            for w in g.leaves():
                if w['type'] in NOUN_PHRASES_TYPES and has_tag_in(w, MASTER_NOUN_TAGS):
                    for tag in TO_ADD:
                        target = w['tags'].get(tag)
                        if target is not None and gtree[target]['type'] in NOUN_PHRASES_TYPES:
                            eq.append(sentence.subpath(target)[0])

            noun_phrases_eq.append(eq)

        sentence.group_words(noun_phrases_eq, kind='noun_phrase')



        # res = {}
        # sent_id = sent["id"]
        # for word in sent["words"]:
        #     term_id = (sent_id, word["id"])
        #     if (word["type"] in NOUN_PHRASES_TYPES
        #        and has_tag_in(word, MASTER_NOUN_TAGS)):
        #         res[term_id] = set()
        #         # add related words
        #         for tag in TO_ADD:
        #             temp = (sent_id, _get_tag(word, tag))
        #             if get_word(temp, sentences)["type"] in NOUN_PHRASES_TYPES:
        #                 res[term_id].append(temp)
        #
        # # ckeck all words in the phrase, in case we have forgotten one
        # for word in sent["words"]:
        #     term_id = (sent_id, word["id"])
        #     if term_id not in res and has_type_in(word, NOUN_PHRASES_TYPES):
        #         for tag in TO_BE_ADDED:
        #             temp = (sent_id, _get_tag(word, tag))
        #             if temp in res:
        #                 if temp != term_id and term_id not in res[temp]:
        #                     res[temp].append(term_id)
        # res_list.append(res)
