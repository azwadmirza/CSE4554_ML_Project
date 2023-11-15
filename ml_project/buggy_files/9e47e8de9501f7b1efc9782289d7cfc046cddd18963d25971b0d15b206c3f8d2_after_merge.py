def get_call_table(blocks, call_table=None, reverse_call_table=None, topological_ordering=True):
    """returns a dictionary of call variables and their references.
    """
    # call_table example: c = np.zeros becomes c:["zeroes", np]
    # reverse_call_table example: c = np.zeros becomes np_var:c
    if call_table is None:
        call_table = {}
    if reverse_call_table is None:
        reverse_call_table = {}

    if topological_ordering:
        order = find_topo_order(blocks)
    else:
        order = list(blocks.keys())

    for label in reversed(order):
        for inst in reversed(blocks[label].body):
            if isinstance(inst, ir.Assign):
                lhs = inst.target.name
                rhs = inst.value
                if isinstance(rhs, ir.Expr) and rhs.op == 'call':
                    call_table[rhs.func.name] = []
                if isinstance(rhs, ir.Expr) and rhs.op == 'getattr':
                    if lhs in call_table:
                        call_table[lhs].append(rhs.attr)
                        reverse_call_table[rhs.value.name] = lhs
                    if lhs in reverse_call_table:
                        call_var = reverse_call_table[lhs]
                        call_table[call_var].append(rhs.attr)
                        reverse_call_table[rhs.value.name] = call_var
                if isinstance(rhs, ir.Global):
                    if lhs in call_table:
                        call_table[lhs].append(rhs.value)
                    if lhs in reverse_call_table:
                        call_var = reverse_call_table[lhs]
                        call_table[call_var].append(rhs.value)
                if isinstance(rhs, ir.FreeVar):
                    if lhs in call_table:
                        call_table[lhs].append(rhs.value)
                    if lhs in reverse_call_table:
                        call_var = reverse_call_table[lhs]
                        call_table[call_var].append(rhs.value)
                if isinstance(rhs, ir.Var):
                    if lhs in call_table:
                        call_table[lhs].append(rhs.name)
                        reverse_call_table[rhs.name] = lhs
                    if lhs in reverse_call_table:
                        call_var = reverse_call_table[lhs]
                        call_table[call_var].append(rhs.name)
            for T, f in call_table_extensions.items():
                if isinstance(inst, T):
                    f(inst, call_table, reverse_call_table)
    return call_table, reverse_call_table