    def get_numeric_data(self, copy=False):
        num_blocks = [b for b in self.blocks
                      if isinstance(b, (IntBlock, FloatBlock))]

        indexer = np.sort(np.concatenate([b.ref_locs for b in num_blocks]))
        new_items = self.items.take(indexer)

        new_blocks = []
        for b in num_blocks:
            b = b.copy(deep=False)
            b.ref_items = new_items
            new_blocks.append(b)
        new_axes = list(self.axes)
        new_axes[0] = new_items
        return BlockManager(new_blocks, new_axes, do_integrity_check=False)