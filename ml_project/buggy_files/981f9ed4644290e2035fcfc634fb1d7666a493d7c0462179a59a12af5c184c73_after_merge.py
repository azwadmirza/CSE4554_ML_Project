    def log_to_term(self, message, verbosity):
        """Write message to stdout/stderr"""
        if verbosity <= 2 or Globals.server:
            termfp = sys.stderr.buffer
        else:
            termfp = sys.stdout.buffer
        tmpstr = self.format(message, self.term_verbosity)
        termfp.write(_to_bytes(tmpstr, encoding=sys.stdout.encoding))