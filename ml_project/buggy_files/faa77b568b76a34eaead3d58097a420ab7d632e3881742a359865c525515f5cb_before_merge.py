def find_potential_aliases(blocks, args):
    aliases = set(args)
    for bl in blocks.values():
        for instr in bl.body:
            if isinstance(instr, ir.Assign):
                expr = instr.value
                lhs = instr.target.name
                if isinstance(expr, ir.Var) and expr.name in aliases:
                    aliases.add(lhs)
    return aliases