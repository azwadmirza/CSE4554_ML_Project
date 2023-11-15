    def log_to_term(self, message, verbosity):
        """Write message to stdout/stderr"""
        if verbosity <= 2 or Globals.server:
            termfp = sys.stderr.buffer
        else:
            termfp = sys.stdout.buffer
        tmpstr = self.format(message, self.term_verbosity)
        if type(tmpstr) == str:  # transform string in bytes
            tmpstr = tmpstr.encode(sys.stdout.encoding, 'backslashreplace')
        termfp.write(tmpstr)