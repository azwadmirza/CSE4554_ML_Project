    def run_commands(self, commands, **kwargs):
        """
        Run commands wrapper
        :param commands: list of commands
        :param kwargs: other args
        :return: list of outputs
        """
        if isinstance(commands, str):
            new_commands = [cli_convert(commands, self.cli_version)]
        else:
            new_commands = [cli_convert(cmd, self.cli_version) for cmd in commands]

        return super(Node, self).run_commands(new_commands, **kwargs)