    def execute(self, cmdstr: str):
        """
            Execute a command string. May raise CommandError.
        """
        parts = list(lexer(cmdstr))
        if not len(parts) >= 1:
            raise exceptions.CommandError("Invalid command: %s" % cmdstr)
        return self.call_strings(parts[0], parts[1:])