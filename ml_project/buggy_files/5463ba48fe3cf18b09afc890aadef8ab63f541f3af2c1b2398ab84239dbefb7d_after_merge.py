    def tree(self, tree):
        if is_working_tree(tree) or tree.tree_root == self.root_dir:
            root = None
        else:
            root = self.root_dir
        self._tree = (
            tree if isinstance(tree, CleanTree) else CleanTree(tree, root)
        )
        # Our graph cache is no longer valid, as it was based on the previous
        # tree.
        self._reset()