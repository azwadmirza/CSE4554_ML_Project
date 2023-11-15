    def load_arguments(self, _):

        from azure.cli.command_modules.interactive.azclishell.color_styles import get_options as style_options

        with self.argument_context('interactive') as c:
            c.argument('style', options_list=['--style', '-s'], help='The colors of the shell.',
                       choices=style_options())