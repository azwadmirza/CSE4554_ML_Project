    def get_samples_in_leaves(self):
        """Get an array of instance indices that belong to each leaf.

        For a given dataset X, separate the instances out into an array, so
        they are grouped together based on what leaf they belong to.

        Examples
        --------
        Given a tree with two leaf nodes ( A <- R -> B ) and the dataset X =
        [ 10, 20, 30, 40, 50, 60 ], where 10, 20 and 40 belong to leaf A, and
        the rest to leaf B, the following structure will be returned (where
        array is the numpy array):
        [array([ 0, 1, 3 ]), array([ 2, 4, 5 ])]

        The first array represents the indices of the values that belong to the
        first leaft, so calling X[ 0, 1, 3 ] = [ 10, 20, 40 ]

        Parameters
        ----------
        data
            A matrix containing the data instances.

        Returns
        -------
        np.array
            The indices of instances belonging to a given leaf.

        """

        def assign(node_id, indices):
            if self._tree.children_left[node_id] == self.NO_CHILD:
                return [indices]
            else:
                feature_idx = self._tree.feature[node_id]
                thresh = self._tree.threshold[node_id]

                column = self.instances.X[indices, feature_idx]
                leftmask = column <= thresh
                leftind = assign(self._tree.children_left[node_id],
                                 indices[leftmask])
                rightind = assign(self._tree.children_right[node_id],
                                  indices[~leftmask])
                return list.__iadd__(leftind, rightind)

        if self._all_leaves is not None:
            return self._all_leaves

        n, _ = self.instances.X.shape

        items = np.arange(n, dtype=int)
        leaf_indices = assign(0, items)
        self._all_leaves = leaf_indices
        return leaf_indices