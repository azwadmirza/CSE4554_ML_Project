    def log_to_term(self, message, verbosity):
        """Write message to stdout/stderr"""
        if verbosity <= 2 or Globals.server:
            termfp = sys.stderr
        else:
            termfp = sys.stdout
        tmpstr = self.format(message, self.term_verbosity)
        if type(tmpstr) != str:  # transform bytes in string
            tmpstr = str(tmpstr, 'utf-8')
        termfp.write(tmpstr)