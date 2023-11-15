    def __init__(self, package, command, return_values, return_code, **kwargs):
        extra = [crayons.blue("Attempted to run command: {0}".format(
            crayons.yellow("$ {0}".format(command), bold=True)
        )),]
        extra.extend([crayons.blue(line.strip()) for line in return_values.splitlines()])
        if isinstance(package, (tuple, list, set)):
            package = " ".join(package)
        message = "{0!s} {1!s}...".format(
            crayons.normal("Failed to uninstall package(s)"),
            crayons.yellow(str(package), bold=True)
        )
        self.exit_code = return_code
        PipenvException.__init__(self, message=fix_utf8(message), extra=extra)
        self.extra = extra