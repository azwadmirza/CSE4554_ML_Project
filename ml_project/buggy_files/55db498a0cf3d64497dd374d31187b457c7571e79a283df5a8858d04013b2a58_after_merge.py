    def _connect(self):
        """Connect to the db and do universal initialization."""
        if self.con is not None:
            return
        # SQLite on Windows on py2 won't open a file if the filename argument
        # has non-ascii characters in it.  Opening a relative file name avoids
        # a problem if the current directory has non-ascii.
        try:
            filename = os.path.relpath(self.filename)
        except ValueError:
            # ValueError can be raised under Windows when os.getcwd() returns a
            # folder from a different drive than the drive of self.filename in
            # which case we keep the original value of self.filename unchanged,
            # hoping that we won't face the non-ascii directory problem.
            filename = self.filename
        # It can happen that Python switches threads while the tracer writes
        # data. The second thread will also try to write to the data,
        # effectively causing a nested context. However, given the idempotent
        # nature of the tracer operations, sharing a connection among threads
        # is not a problem.
        if self.debug:
            self.debug.write("Connecting to {!r}".format(self.filename))
        self.con = sqlite3.connect(filename, check_same_thread=False)
        self.con.create_function('REGEXP', 2, _regexp)

        # This pragma makes writing faster. It disables rollbacks, but we never need them.
        # PyPy needs the .close() calls here, or sqlite gets twisted up:
        # https://bitbucket.org/pypy/pypy/issues/2872/default-isolation-mode-is-different-on
        self.execute("pragma journal_mode=off").close()
        # This pragma makes writing faster.
        self.execute("pragma synchronous=off").close()