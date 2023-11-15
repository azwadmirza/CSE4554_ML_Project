def add_offset_to_labels(blocks, offset):
    """add an offset to all block labels and jump/branch targets
    """
    new_blocks = {}
    for l,b in blocks.items():
        term = b.body[-1]
        if isinstance(term, ir.Jump):
            term.target += offset
        if isinstance(term, ir.Branch):
            term.truebr += offset
            term.falsebr += offset
        new_blocks[l+offset] = b
    return new_blocks