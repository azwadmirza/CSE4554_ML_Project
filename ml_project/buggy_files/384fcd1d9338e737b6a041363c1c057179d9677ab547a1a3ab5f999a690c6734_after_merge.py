    def append(self, cmd):
        if not self.remember_history:
            return
        envs = builtins.__xonsh__.env
        inp = cmd["inp"].rstrip()
        self.inps.append(inp)
        self.outs.append(cmd.get("out"))
        self.rtns.append(cmd["rtn"])
        self.tss.append(cmd.get("ts", (None, None)))

        opts = envs.get("HISTCONTROL")
        if "ignoredups" in opts and inp == self._last_hist_inp:
            # Skipping dup cmd
            return
        if "ignoreerr" in opts and cmd["rtn"] != 0:
            # Skipping failed cmd
            return
        if "ignorespace" in opts and cmd.get("spc"):
            # Skipping cmd starting with space
            return

        try:
            del cmd["spc"]
        except KeyError:
            pass
        self._last_hist_inp = inp
        try:
            xh_sqlite_append_history(
                cmd,
                str(self.sessionid),
                store_stdout=envs.get("XONSH_STORE_STDOUT", False),
                filename=self.filename,
                remove_duplicates=("erasedups" in opts),
            )
        except sqlite3.OperationalError as err:
            print(f"SQLite History Backend Error: {err}")