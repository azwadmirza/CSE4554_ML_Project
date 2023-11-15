def get_tuple_table(blocks, tuple_table=None):
    """returns a dictionary of tuple variables and their values.
    """
    if tuple_table is None:
        tuple_table = {}

    for block in blocks.values():
        for inst in block.body:
            if isinstance(inst, ir.Assign):
                lhs = inst.target.name
                rhs = inst.value
                if isinstance(rhs, ir.Expr) and rhs.op == 'build_tuple':
                    tuple_table[lhs] = rhs.items
                if isinstance(rhs, ir.Const) and isinstance(rhs.value, tuple):
                    tuple_table[lhs] = rhs.value
            for T, f in tuple_table_extensions.items():
                if isinstance(inst, T):
                    f(inst, tuple_table)
    return tuple_table