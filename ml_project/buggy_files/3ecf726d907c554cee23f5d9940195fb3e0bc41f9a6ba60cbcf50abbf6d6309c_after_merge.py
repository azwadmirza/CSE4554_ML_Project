    def add_arguments(self, parser):
        self.instances = {}

        if self.subcommands:
            subparsers = parser.add_subparsers(dest=self.subcommand_dest)
            for command, cls in self.subcommands.items():
                instance = cls(self.stdout._out, self.stderr._out)
                instance.style = self.style
                parser_sub = subparsers.add_parser(
                    cmd=self, name=instance.command_name, help=instance.help_string,
                    description=instance.help_string
                )

                add_builtin_arguments(parser=parser_sub)
                instance.add_arguments(parser_sub)
                self.instances[command] = instance