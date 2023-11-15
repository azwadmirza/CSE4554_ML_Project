def get_array_accesses(blocks, accesses=None):
    """returns a dictionary of arrays accessed and their indices.
    """
    if accesses is None:
        accesses = {}

    for block in blocks.values():
        for inst in block.body:
            if isinstance(inst, ir.SetItem):
                accesses[inst.target.name] = inst.index.name
            if isinstance(inst, ir.StaticSetItem):
                accesses[inst.target.name] = inst.index_var.name
            if isinstance(inst, ir.Assign):
                lhs = inst.target.name
                rhs = inst.value
                if isinstance(rhs, ir.Expr) and rhs.op == 'getitem':
                    accesses[rhs.value.name] = rhs.index.name
                if isinstance(rhs, ir.Expr) and rhs.op == 'static_getitem':
                    accesses[rhs.value.name] = rhs.index_var.name
            for T, f in array_accesses_extensions.items():
                if isinstance(inst, T):
                    f(inst, accesses)
    return accesses