    def __init__(self, opts):
        super().__init__(opts)

        self.start_err: typing.Optional[log.LogEntry] = None

        self.view: view.View = view.View()
        self.events = eventstore.EventStore()
        self.events.sig_add.connect(self.sig_add_log)

        self.stream_path = None
        self.keymap = keymap.Keymap(self)
        defaultkeys.map(self.keymap)
        self.options.errored.connect(self.options_error)

        self.view_stack = []

        signals.call_in.connect(self.sig_call_in)
        self.addons.add(*addons.default_addons())
        self.addons.add(
            intercept.Intercept(),
            self.view,
            self.events,
            consoleaddons.UnsupportedLog(),
            readfile.ReadFile(),
            consoleaddons.ConsoleAddon(self),
            keymap.KeymapConfig(),
        )

        def sigint_handler(*args, **kwargs):
            self.prompt_for_exit()

        signal.signal(signal.SIGINT, sigint_handler)

        self.window = None