    def run(self):
        self.ui = urwid.raw_display.Screen()
        self.ui.set_terminal_properties(256)
        self.set_palette(self.palette)
        self.loop = urwid.MainLoop(
            urwid.SolidFill("x"),
            screen = self.ui,
            handle_mouse = not self.options.no_mouse,
        )

        if self.options.rfile:
            ret = self.load_flows_path(self.options.rfile)
            if ret and self.state.flow_count():
                signals.add_event(
                    "File truncated or corrupted. "
                    "Loaded as many flows as possible.",
                    "error"
                )
            elif ret and not self.state.flow_count():
                self.shutdown()
                print("Could not load file: {}".format(ret), file=sys.stderr)
                sys.exit(1)

        self.loop.set_alarm_in(0.01, self.ticker)
        if self.server.config.http2 and not tcp.HAS_ALPN:  # pragma: no cover
            def http2err(*args, **kwargs):
                signals.status_message.send(
                    message = "HTTP/2 disabled - OpenSSL 1.0.2+ required."
                              " Use --no-http2 to silence this warning.",
                    expire=5
                )
            self.loop.set_alarm_in(0.01, http2err)

        # It's not clear why we need to handle this explicitly - without this,
        # mitmproxy hangs on keyboard interrupt. Remove if we ever figure it
        # out.
        def exit(s, f):
            raise urwid.ExitMainLoop
        signal.signal(signal.SIGINT, exit)

        self.loop.set_alarm_in(
            0.0001,
            lambda *args: self.view_flowlist()
        )

        self.start()
        try:
            self.loop.run()
        except Exception:
            self.loop.stop()
            sys.stdout.flush()
            print(traceback.format_exc(), file=sys.stderr)
            print("mitmproxy has crashed!", file=sys.stderr)
            print("Please lodge a bug report at:", file=sys.stderr)
            print("\thttps://github.com/mitmproxy/mitmproxy", file=sys.stderr)
            print("Shutting down...", file=sys.stderr)
        sys.stderr.flush()
        self.shutdown()