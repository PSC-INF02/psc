import sys
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

    # Todo: cache
    def path(self):
        path = []
        root = self
        while root.parent is not None:
            path.append(root.id)
            root = root.parent
        path.reverse()
        return path

    def subpath(self, path):
        rpath = self.path()
        d = len(rpath)

        if rpath == path[:d]:
            return path[d:]
        else:
            raise IndexError("%s (%s) is not a path of tree %s (%s)" % (str(path), self.root[path]['text'], str(rpath), self.root[rpath]['text']))

    def contains_path(self, path):
        rpath = self.path()
        d = len(rpath)
        return rpath == path[:d]


    def relation_tags(self):
        for tag, path in self['tags'].items():
            if is_relation_tag(tag):
                yield (tag, path)



    def group_children(self, groups, flatten_singletons=True):
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
        flat_singletons = set(range(len(self.children)))
        if flatten_singletons:
            # Flatten all singleton groups
            for i in range(len(self.children)):
                j = uf[i]
                if i != j:
                    flat_singletons.discard(i)
                    flat_singletons.discard(j)
        else:
            # Flatten only singletons of objects not in groups
            flat_singletons.difference_update(x for g in groups for x in g)

        # Map an id from each (non-singleton) equivalence class to a new empty tree
        group_map = {i:GrammarTree() for i in range(len(self.children)) if uf[i] == i and i not in flat_singletons}
        new_groups = list(group_map.values())

        # Add each object to its group, and reconstruct the tree
        children = self.children
        self.children = []
        # added_groups = set()
        id_map = {}
        for i, o in enumerate(children):
            if i in flat_singletons:
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

    def group_words(self, groups, merge_tags=False, kind=None, flatten_singletons=True):
        id_map, new_groups = self.group_children(groups, flatten_singletons)

        path = self.path()
        d = len(self.path())

        # Redirect tags to new ids
        for n in self.root.nodes():
            if 'tags' in n:
                for tag, val in n.relation_tags():
                    if val[:d] == path:
                        n['tags'][tag] = val[:d] + id_map[val[d]] + val[d + 1:]
            if 'relations' in n:
                for i, r in enumerate(n['relations']):
                    if r[:d] == path:
                        n['relations'][i] = r[:d] + id_map[r[d]] + r[d + 1:]

        # Compute node text from descendants
        for x in new_groups:
            if hasattr(x, 'children'):
                x['text'] = " ".join(y['text'] for y in x.children)

        if merge_tags:
            for g in new_groups:
                tags = {}
                for x in g:
                    # if 'tags' in x:
                    for tag, val in x['tags'].items():
                        if tag not in tags:
                            tags[tag] = val
                        elif tags[tag] != val:  # Conflicting values
                            tags[tag] = None

                g['tags'] = {}
                for tag, val in tags.items():
                    if val is not None and not (is_relation_tag(tag) and g.contains_path(val)):
                        g['tags'][tag] = tags[tag]


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


class GrammarTreeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GrammarTree):
            o = obj.contents.copy()
            if obj.id is not None:
                o['id'] = obj.id

            # Make relations human-readable
            for tag, path in o.get('tags', {}).items():
                if is_relation_tag(tag):
                    o['tags'][tag] = ", ".join(map(str, path)) + ": " + obj.root[path]['text']

            if isinstance(obj, Word):
                if 'relations' in o:
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
        # Group compound propernouns
        propernoun_eq = []
        for w in sentence:
            if w['type'] in PROPERNOUNS:
                for tag, path in w.relation_tags():
                    if tag in PROPERNOUNS_RELATIONS:
                        try:
                            propernoun_eq.append([w.id, sentence.subpath(path)[0]])
                        except IndexError as ex:  # target is not in the same sentence
                            print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'compound_propernoun', str(ex)), file=sys.stderr)

        propernouns = sentence.group_words(propernoun_eq, kind='compound_propernoun', merge_tags=True)
        for n in propernouns:
            if any(w['tags'].get('HUMAN') for w in n):
                n['tags']['HUMAN'] = True


        # Group noun phrases
        noun_phrases_eq = []
        head_nouns = set()
        for w in sentence:
            if w['kind'] in NOUN_PHRASE_TYPES and not set(HEAD_NOUN_TAGS).isdisjoint(w['tags']):
                head_nouns.add(w.id)
                eq = [w.id]
                for tag in RELATED_FROM_HEAD_NOUN_TAGS:
                    target = w['tags'].get(tag)
                    if target is not None and w.root[target]['kind'] in NOUN_PHRASE_TYPES:
                        try:
                            eq.append(sentence.subpath(target)[0])
                        except IndexError as ex:  # target is not in the same sentence
                            print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'noun_phrase', str(ex)), file=sys.stderr)
                noun_phrases_eq.append(eq)

        for w in sentence:
            if w['kind'] in NOUN_PHRASE_TYPES:
                for tag in RELATED_TO_HEAD_NOUN_TAGS:
                    target = w['tags'].get(tag)
                    if target is not None:
                        try:
                            target = sentence.subpath(target)[0]
                            if target in head_nouns:
                                noun_phrases_eq.append([w.id, target])
                        except IndexError as ex:  # target is not in the same sentence
                            print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'noun_phrase', str(ex)), file=sys.stderr)

        noun_phrases = sentence.group_words(noun_phrases_eq, kind='noun_phrase', merge_tags=True)
        for np in noun_phrases:
            head_nouns = []
            for w in np:
                if w['kind'] in NOUN_PHRASE_TYPES and not set(HEAD_NOUN_TAGS).isdisjoint(w['tags']):
                    head_nouns.append(w.path())
            np['tags']['HEAD_NOUN'] = head_nouns[0]


        # Group verb phrases
        verb_phrases_eq = []
        head_verbs = set()
        for w in sentence:
            if w['kind'] in VERB_PHRASE_TYPES and not set(HEAD_VERB_TAGS).isdisjoint(w['tags']):
                head_verbs.add(w.id)
                eq = [w.id]
                for tag in RELATED_FROM_HEAD_VERB_TAGS:
                    target = w['tags'].get(tag)
                    if target is not None and w.root[target]['kind'] in VERB_PHRASE_TYPES:
                        try:
                            eq.append(sentence.subpath(target)[0])
                        except IndexError as ex:  # target is not in the same sentence
                            print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'noun_phrase', str(ex)), file=sys.stderr)

                verb_phrases_eq.append(eq)

        for w in sentence:
            if w['kind'] in VERB_PHRASE_TYPES:
                for tag in RELATED_TO_HEAD_VERB_TAGS:
                    target = w['tags'].get(tag)
                    if target is not None:
                        try:
                            target = sentence.subpath(target)[0]
                            if target in head_verbs:
                                verb_phrases_eq.append([w.id, target])
                        except IndexError as ex:  # target is not in the same sentence
                            print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'verb_phrase', str(ex)), file=sys.stderr)


        verb_phrases = sentence.group_words(verb_phrases_eq, kind='verb_phrase', merge_tags=True)
        for vp in verb_phrases:
            head_verbs = []
            for w in vp:
                if w['kind'] in VERB_PHRASE_TYPES and not set(HEAD_VERB_TAGS).isdisjoint(w['tags']):
                    head_verbs.append(w.path())
            vp['tags']['HEAD_VERB'] = head_verbs[0]


        # Use given 'relations' attribute
        relations_eq = []
        for w in sentence.leaves():
            if 'relations' in w:
                eq = []
                for rel in w["relations"]:
                    try:
                        eq.append(sentence.subpath(rel)[0])
                    except IndexError as ex:  # target is not in the same sentence
                        print("Warning while merging word '%s' in a %s: %s" % (w['text'], 'syntagme', str(ex)), file=sys.stderr)
                relations_eq.append(eq)
                del w['relations']

        sentence.group_words(relations_eq, kind='syntagme')
