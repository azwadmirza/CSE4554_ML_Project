    def validateMasterArgument(self, master_arg):
        """
        Parse the <master> argument.

        @param master_arg: the <master> argument to parse

        @return: tuple of master's host and port
        @raise UsageError: on errors parsing the argument
        """
        if master_arg[:5] == "http:":
            raise usage.UsageError("<master> is not a URL - do not use URL")

        if master_arg.startswith("[") and "]" in master_arg:
            # detect ipv6 address with format [2001:1:2:3:4::1]:4321
            master, port_tmp = master_arg.split("]")
            master = master[1:]
            if ":" not in port_tmp:
                port = 9989
            else:
                port = port_tmp.split(":")[1]

        elif ":" not in master_arg:
            master = master_arg
            port = 9989
        else:
            try:
                master, port = master_arg.split(":")
            except ValueError:
                raise usage.UsageError("invalid <master> argument '{}', "
                                       "if it is an ipv6 address, it must be enclosed by []".format(master_arg))

        if not master:
            raise usage.UsageError("invalid <master> argument '{}'".format(
                                   master_arg))
        try:
            port = int(port)
        except ValueError:
            raise usage.UsageError("invalid master port '{}', "
                                   "needs to be a number".format(port))

        return master, port