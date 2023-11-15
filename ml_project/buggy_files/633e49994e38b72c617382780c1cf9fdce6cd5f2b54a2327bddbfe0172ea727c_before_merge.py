    def from_blocks(cls, blocks, index):
        # also checks for overlap
        items = _union_block_items(blocks)
        ndim = blocks[0].ndim
        return BlockManager(blocks, [items, index])