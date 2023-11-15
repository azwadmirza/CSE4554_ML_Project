    def clear(self):
        """Clears the current session's history from both memory and disk."""
        # Wipe memory
        self.inps = []
        self.rtns = []
        self.outs = []
        self.tss = []

        # Wipe the current session's entries from the database.
        sql = "DELETE FROM xonsh_history WHERE sessionid = ?"
        with _xh_sqlite_get_conn(filename=self.filename) as conn:
            c = conn.cursor()
            _xh_sqlite_create_history_table(c)
            c.execute(sql, (str(self.sessionid),))