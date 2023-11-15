    def __init__(self, cli_ctx, style=None, completer=None,
                 lexer=None, history=None,
                 input_custom=sys.stdin, output_custom=None,
                 user_feedback=False, intermediate_sleep=.25, final_sleep=4):

        from .color_styles import style_factory

        self.cli_ctx = cli_ctx
        self.config = Configuration(cli_ctx.config, style=style)
        self.config.set_style(style)
        self.style = style_factory(self.config.get_style())
        self.lexer = lexer or get_az_lexer(self.config) if self.style else None
        try:
            self.completer = completer or AzCompleter(self, GatherCommands(self.config))
            self.completer.initialize_command_table_attributes()
        except IOError:  # if there is no cache
            self.completer = AzCompleter(self, None)
        self.history = history or FileHistory(os.path.join(self.config.config_dir, self.config.get_history()))
        os.environ[ENV_ADDITIONAL_USER_AGENT] = 'AZURECLISHELL/' + __version__

        # OH WHAT FUN TO FIGURE OUT WHAT THESE ARE!
        self._cli = None
        self.layout = None
        self.description_docs = u''
        self.param_docs = u''
        self.example_docs = u''
        self.last = None
        self.last_exit = 0
        self.user_feedback = user_feedback
        self.input = input_custom
        self.output = output_custom
        self.config_default = ""
        self.default_command = ""
        self.threads = []
        self.curr_thread = None
        self.spin_val = -1
        self.intermediate_sleep = intermediate_sleep
        self.final_sleep = final_sleep
        self.command_table_thread = None

        # try to consolidate state information here...
        # Used by key bindings and layout
        self.example_page = 1
        self.is_prompting = False
        self.is_example_repl = False
        self.is_showing_default = False
        self.is_symbols = True