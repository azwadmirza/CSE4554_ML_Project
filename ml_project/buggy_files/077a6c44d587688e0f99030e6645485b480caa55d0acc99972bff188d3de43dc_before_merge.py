    def copy(self):
        """Copy the this node tree

        Note all references to readers are removed. This is meant to avoid
        tree copies accessing readers that would return incompatible (Area)
        data. Theoretically it should be possible for tree copies to request
        compositor or modifier information as long as they don't depend on
        any datasets not already existing in the dependency tree.
        """
        new_tree = DependencyTree({}, self.compositors, self.modifiers)
        for c in self.children:
            c = c.copy()
            new_tree.add_child(new_tree, c)
        new_tree._all_nodes = new_tree.flatten(d=self._all_nodes)
        return new_tree