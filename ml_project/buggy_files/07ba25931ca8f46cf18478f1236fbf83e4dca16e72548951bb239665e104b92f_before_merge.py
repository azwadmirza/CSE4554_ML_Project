    def read(self, nodes=None, **kwargs):
        """Load datasets from the necessary reader.

        Args:
            nodes (iterable): DependencyTree Node objects
            **kwargs: Keyword arguments to pass to the reader's `load` method.

        Returns:
            DatasetDict of loaded datasets

        """
        if nodes is None:
            required_nodes = self.wishlist - set(self.datasets.keys())
            nodes = self.dep_tree.leaves(nodes=required_nodes)
        return self.read_datasets(nodes, **kwargs)