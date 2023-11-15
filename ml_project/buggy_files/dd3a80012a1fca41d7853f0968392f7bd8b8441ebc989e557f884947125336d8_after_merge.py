    def __init__(self, tree, sentence=None, highlight=()):
        if sentence is None:
            leaves = tree.leaves()
            if (
                leaves
                and not any(len(a) == 0 for a in tree.subtrees())
                and all(isinstance(a, int) for a in leaves)
            ):
                sentence = [str(a) for a in leaves]
            else:
                # this deals with empty nodes (frontier non-terminals)
                # and multiple/mixed terminals under non-terminals.
                tree = tree.copy(True)
                sentence = []
                for a in tree.subtrees():
                    if len(a) == 0:
                        a.append(len(sentence))
                        sentence.append(None)
                    elif any(not isinstance(b, Tree) for b in a):
                        for n, b in enumerate(a):
                            if not isinstance(b, Tree):
                                a[n] = len(sentence)
                                if type(b) == tuple:
                                    b = '/'.join(b)
                                sentence.append('%s' % b)
        self.nodes, self.coords, self.edges, self.highlight = self.nodecoords(
            tree, sentence, highlight
        )