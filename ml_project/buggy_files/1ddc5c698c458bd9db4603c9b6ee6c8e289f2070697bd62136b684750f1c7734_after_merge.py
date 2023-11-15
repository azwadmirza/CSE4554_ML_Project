def add_offset_to_labels(blocks, offset):
    """add an offset to all block labels and jump/branch targets
    """
    new_blocks = {}
    for l, b in blocks.items():
        # some parfor last blocks might be empty
        term = None
        if b.body:
            term = b.body[-1]
            for inst in b.body:
                for T, f in add_offset_to_labels_extensions.items():
                    if isinstance(inst, T):
                        f_max = f(inst, offset)
        if isinstance(term, ir.Jump):
            term.target += offset
        if isinstance(term, ir.Branch):
            term.truebr += offset
            term.falsebr += offset
        new_blocks[l + offset] = b
    return new_blocks