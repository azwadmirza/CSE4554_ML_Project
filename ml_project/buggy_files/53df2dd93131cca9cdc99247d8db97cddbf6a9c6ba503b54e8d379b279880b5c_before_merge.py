    def write(cls, s, file=sys.stdout, end="\n"):
        """
        Print a message via tqdm (without overlap with bars)
        """
        fp = file

        # Clear all bars
        inst_cleared = []
        for inst in getattr(cls, '_instances', []):
            # Clear instance if in the target output file
            # or if write output + tqdm output are both either
            # sys.stdout or sys.stderr (because both are mixed in terminal)
            if inst.fp == fp or all(f in (sys.stdout, sys.stderr)
                                    for f in (fp, inst.fp)):
                inst.clear()
                inst_cleared.append(inst)
        # Write the message
        fp.write(s)
        fp.write(end)
        # Force refresh display of bars we cleared
        for inst in inst_cleared:
            inst.refresh()