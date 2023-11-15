    def tree(self, tree):
        self._tree = tree if isinstance(tree, CleanTree) else CleanTree(tree)
        # Our graph cache is no longer valid, as it was based on the previous
        # tree.
        self._reset()