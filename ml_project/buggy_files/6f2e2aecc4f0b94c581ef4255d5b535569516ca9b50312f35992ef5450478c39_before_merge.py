def parfor_defs(parfor):
    """list variables written in this parfor by recursively
    calling compute_use_defs() on body and combining block defs.
    """
    all_defs = set()
    # index variables are sematically defined here
    for l in parfor.loop_nests:
        all_defs.add(l.index_variable.name)

    # all defs of body blocks
    for l,b in parfor.loop_body.items():
        for stmt in b.body:
            if isinstance(stmt, ir.Assign):
                all_defs.add(stmt.target.name)
            elif isinstance(stmt, Parfor):
                all_defs.update(parfor_defs(stmt))

    # all defs of init block
    for stmt in parfor.init_block.body:
        if isinstance(stmt, ir.Assign):
            all_defs.add(stmt.target.name)
        elif isinstance(stmt, Parfor):
            all_defs.update(parfor_defs(stmt))

    return all_defs