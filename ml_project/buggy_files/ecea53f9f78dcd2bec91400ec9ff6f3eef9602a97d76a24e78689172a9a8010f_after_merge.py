    def __init__(self, tree, tree_root=None):
        self.tree = tree
        if tree_root:
            self._tree_root = tree_root
        else:
            self._tree_root = self.tree.tree_root