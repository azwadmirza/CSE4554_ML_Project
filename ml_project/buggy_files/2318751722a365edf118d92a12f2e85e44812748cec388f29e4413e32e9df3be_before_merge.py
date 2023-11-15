    def run(self):
        if not sys.stdout.isatty():
            print("Error: mitmproxy's console interface requires a tty. "
                  "Please run mitmproxy in an interactive shell environment.", file=sys.stderr)
            sys.exit(1)

        self.ui = window.Screen()
        self.ui.set_terminal_properties(256)
        self.set_palette(self.options, None)
        self.options.subscribe(
            self.set_palette,
            ["console_palette", "console_palette_transparent"]
        )
        self.loop = urwid.MainLoop(
            urwid.SolidFill("x"),
            event_loop=urwid.AsyncioEventLoop(loop=asyncio.get_event_loop()),
            screen = self.ui,
            handle_mouse = self.options.console_mouse,
        )
        self.window = window.Window(self)
        self.loop.widget = self.window
        self.window.refresh()

        if self.start_err:
            def display_err(*_):
                self.sig_add_log(None, self.start_err)
                self.start_err = None
            self.loop.set_alarm_in(0.01, display_err)

        super().run_loop(self.loop.run)