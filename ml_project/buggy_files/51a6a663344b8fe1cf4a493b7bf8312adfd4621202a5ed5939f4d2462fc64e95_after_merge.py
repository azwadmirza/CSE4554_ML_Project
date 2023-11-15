    def compute(self, nodes=None):
        """Compute all the composites contained in `requirements`.
        """
        if nodes is None:
            required_nodes = self.wishlist - set(self.datasets.keys())
            nodes = set(self.dep_tree.trunk(nodes=required_nodes)) - \
                set(self.datasets.keys())
        return self._read_composites(nodes)