    def same_exit_point(loop):
        "all exits must point to the same location"
        outedges = set()
        for k in loop.exits:
            outedges |= set(x for x, _ in cfg.successors(k))
        return len(outedges) == 1