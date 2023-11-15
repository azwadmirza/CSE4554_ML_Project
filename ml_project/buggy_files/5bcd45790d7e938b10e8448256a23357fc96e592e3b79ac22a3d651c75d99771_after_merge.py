    def load_command_table(self, _):

        with self.command_group('', operations_tmpl='azure.cli.command_modules.interactive#{}') as g:
            g.command('interactive', 'start_shell')
        return self.command_table