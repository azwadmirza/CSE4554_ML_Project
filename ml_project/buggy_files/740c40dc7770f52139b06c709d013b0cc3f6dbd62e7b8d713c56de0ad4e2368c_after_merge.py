    def same_exit_point(loop):
        "all exits must point to the same location"
        outedges = set()
        for k in loop.exits:
            succs = set(x for x, _ in cfg.successors(k))
            if not succs:
                # If the exit point has no successor, it contains an return
                # statement, which is not handled by the looplifting code.
                # Thus, this loop is not a candidate.
                _logger.debug("return-statement in loop.")
                return False
            outedges |= succs
        ok = len(outedges) == 1
        _logger.debug("same_exit_point=%s (%s)", ok, outedges)
        return ok