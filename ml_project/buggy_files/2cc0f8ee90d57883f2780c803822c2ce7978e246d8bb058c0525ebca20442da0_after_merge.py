    def clear(self):
        """Clears the current session's history from both memory and disk."""
        # Wipe memory
        self.inps = []
        self.rtns = []
        self.outs = []
        self.tss = []

        xh_sqlite_wipe_session(sessionid=self.sessionid, filename=self.filename)