def get_parfor_outputs(parfor, parfor_params):
    """get arrays that are written to inside the parfor and need to be passed
    as parameters to gufunc.
    """
    # FIXME: The following assumes the target of all SetItem are outputs,
    # which is wrong!
    last_label = max(parfor.loop_body.keys())
    outputs = []
    for blk in parfor.loop_body.values():
        for stmt in blk.body:
            if isinstance(stmt, ir.SetItem):
                if stmt.index.name == parfor.index_var.name:
                    outputs.append(stmt.target.name)
    # make sure these written arrays are in parfor parameters (live coming in)
    outputs = list(set(outputs) & set(parfor_params))
    return sorted(outputs)