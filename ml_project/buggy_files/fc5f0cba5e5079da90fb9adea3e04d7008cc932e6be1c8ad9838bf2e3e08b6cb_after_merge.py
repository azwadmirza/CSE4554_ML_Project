    def _setitem_with_indexer(self, indexer, value):
        # also has the side effect of consolidating in-place
        if self.obj._is_mixed_type:
            if not isinstance(indexer, tuple):
                indexer = self._tuplify(indexer)

            het_axis = self.obj._het_axis
            het_idx = indexer[het_axis]

            if isinstance(het_idx, (int, long)):
                het_idx = [het_idx]

            plane_indexer = indexer[:het_axis] + indexer[het_axis + 1:]
            item_labels = self.obj._get_axis(het_axis)
            for item in item_labels[het_idx]:
                data = self.obj[item]
                data.values[plane_indexer] = value
        else:
            if isinstance(indexer, tuple):
                indexer = _maybe_convert_ix(*indexer)
            self.obj.values[indexer] = value