    def execute(self, cmdstr: str):
        """
            Execute a command string. May raise CommandError.
        """
        try:
            parts = list(lexer(cmdstr))
        except ValueError as e:
            raise exceptions.CommandError("Command error: %s" % e)
        if not len(parts) >= 1:
            raise exceptions.CommandError("Invalid command: %s" % cmdstr)
        return self.call_strings(parts[0], parts[1:])