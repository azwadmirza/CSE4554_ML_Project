        def assign(node_id, indices):
            if self._tree.children_left[node_id] == self.NO_CHILD:
                return [indices]
            else:
                feature_idx = self._tree.feature[node_id]
                thresh = self._tree.threshold[node_id]

                column = self.instances_transformed.X[indices, feature_idx]
                leftmask = column <= thresh
                leftind = assign(self._tree.children_left[node_id],
                                 indices[leftmask])
                rightind = assign(self._tree.children_right[node_id],
                                  indices[~leftmask])
                return list.__iadd__(leftind, rightind)