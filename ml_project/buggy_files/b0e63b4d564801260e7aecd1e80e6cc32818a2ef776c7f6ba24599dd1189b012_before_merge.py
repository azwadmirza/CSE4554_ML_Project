    def validateMasterArgument(self, master_arg):
        """
        Parse the <master> argument.

        @param master_arg: the <master> argument to parse

        @return: tuple of master's host and port
        @raise UsageError: on errors parsing the argument
        """
        if master_arg[:5] == "http:":
            raise usage.UsageError("<master> is not a URL - do not use URL")

        if ":" not in master_arg:
            master = master_arg
            port = 9989
        else:
            master, port = master_arg.split(":")

        if not master:
            raise usage.UsageError("invalid <master> argument '{}'".format(
                                   master_arg))
        try:
            port = int(port)
        except ValueError:
            raise usage.UsageError("invalid master port '{}', "
                                   "needs to be a number".format(port))

        return master, port