    def from_blocks(cls, blocks, index):
        # also checks for overlap
        items = _union_block_items(blocks)
        for blk in blocks:
            blk.ref_items = items
        return BlockManager(blocks, [items, index])