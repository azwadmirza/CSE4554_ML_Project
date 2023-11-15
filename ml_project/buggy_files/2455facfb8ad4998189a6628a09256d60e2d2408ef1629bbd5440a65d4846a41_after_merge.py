    def reindex_axis(self, new_axis, method=None, axis=0, copy=True):
        new_axis = _ensure_index(new_axis)
        cur_axis = self.axes[axis]

        if new_axis.equals(cur_axis):
            if copy:
                result = self.copy(deep=True)
                result.axes[axis] = new_axis

                if axis == 0:
                    # patch ref_items, #1823
                    for blk in result.blocks:
                        blk.ref_items = new_axis

                return result
            else:
                return self

        if axis == 0:
            assert(method is None)
            return self.reindex_items(new_axis)

        new_axis, indexer = cur_axis.reindex(new_axis, method)
        return self.reindex_indexer(new_axis, indexer, axis=axis)