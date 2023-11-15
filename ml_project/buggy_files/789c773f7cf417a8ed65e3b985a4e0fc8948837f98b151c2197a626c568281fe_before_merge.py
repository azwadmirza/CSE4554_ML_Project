def find_topo_order(blocks, cfg = None):
    """find topological order of blocks such that true branches are visited
    first (e.g. for_break test in test_dataflow).
    """
    if cfg == None:
        cfg = compute_cfg_from_blocks(blocks)
    post_order = []
    seen = set()

    def _dfs_rec(node):
        if node not in seen:
            seen.add(node)
            succs = cfg._succs[node]
            last_inst = blocks[node].body[-1]
            if isinstance(last_inst, ir.Branch):
                succs = [last_inst.falsebr, last_inst.truebr]
            for dest in succs:
                if (node, dest) not in cfg._back_edges:
                    _dfs_rec(dest)
            post_order.append(node)

    _dfs_rec(cfg.entry_point())
    post_order.reverse()
    return post_order