    def dump(self):
        """Write the cached history to external storage."""
        opts = builtins.__xonsh__.env.get("HISTCONTROL")
        last_inp = None
        cmds = []
        for cmd in self.buffer:
            if "ignoredups" in opts and cmd["inp"] == last_inp:
                # Skipping dup cmd
                if self.skip is not None:
                    self.skip(1)
                continue
            if "ignoreerr" in opts and cmd["rtn"] != 0:
                # Skipping failed cmd
                if self.skip is not None:
                    self.skip(1)
                continue
            cmds.append(cmd)
            last_inp = cmd["inp"]
        with open(self.filename, "r", newline="\n") as f:
            hist = xlj.LazyJSON(f).load()
        load_hist_len = len(hist["cmds"])
        hist["cmds"].extend(cmds)
        if self.at_exit:
            hist["ts"][1] = time.time()  # apply end time
            hist["locked"] = False
        if not builtins.__xonsh__.env.get("XONSH_STORE_STDOUT", False):
            [cmd.pop("out") for cmd in hist["cmds"][load_hist_len:] if "out" in cmd]
        with open(self.filename, "w", newline="\n") as f:
            xlj.ljdump(hist, f, sort_keys=True)