    def run_commands(self, commands, **kwargs):
        """
        Run commands wrapper
        :param commands: list of commands
        :param kwargs: other args
        :return: list of outputs
        """
        fn0039_transform = kwargs.pop("fn0039_transform", True)
        if fn0039_transform:
            if isinstance(commands, str):
                commands = [cli_convert(commands, self.cli_version)]
            else:
                commands = [cli_convert(cmd, self.cli_version) for cmd in commands]

        return super(Node, self).run_commands(commands, **kwargs)