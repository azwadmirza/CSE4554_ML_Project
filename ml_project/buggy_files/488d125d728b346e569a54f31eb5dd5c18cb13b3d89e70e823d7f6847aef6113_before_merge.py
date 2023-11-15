    def call(self):
        """
        """
        escape_fn = lambda s: s
        newline = True

        try:
            optlist, args = getopt.getopt(self.args, "eEn")
            for opt in optlist:
                if opt[0] == '-e':
                    escape_fn = functools.partial(str.decode, encoding="string_escape")
                elif opt[0] == '-E':
                    escape_fn = lambda s: s
                elif opt[0] == '-n':
                    newline = False
        except:
            args = self.args

        # FIXME: Wrap in exception, Python escape cannot handle single digit \x codes (e.g. \x1)
        try:
            self.write(escape_fn(' '.join(args)))
        except ValueError as e:
            log.msg("echo command received Python incorrect hex escape")

        if newline is True:
            self.write('\n')