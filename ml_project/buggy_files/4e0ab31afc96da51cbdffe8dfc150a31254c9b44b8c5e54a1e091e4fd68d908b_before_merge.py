    def __init__(self, server, options):
        flow.FlowMaster.__init__(self, options, server, flow.State())
        self.has_errored = False
        self.addons.add(options, *builtins.default_addons())
        self.addons.add(options, dumper.Dumper())
        # This line is just for type hinting
        self.options = self.options  # type: Options
        self.server_replay_ignore_params = options.server_replay_ignore_params
        self.server_replay_ignore_content = options.server_replay_ignore_content
        self.server_replay_ignore_host = options.server_replay_ignore_host
        self.refresh_server_playback = options.refresh_server_playback
        self.server_replay_ignore_payload_params = options.server_replay_ignore_payload_params

        self.set_stream_large_bodies(options.stream_large_bodies)

        if self.server and self.options.http2 and not tcp.HAS_ALPN:  # pragma: no cover
            print("ALPN support missing (OpenSSL 1.0.2+ required)!\n"
                  "HTTP/2 is disabled. Use --no-http2 to silence this warning.",
                  file=sys.stderr)

        if options.client_replay:
            self.start_client_playback(
                self._readflow(options.client_replay),
                not options.keepserving
            )

        if options.rfile:
            try:
                self.load_flows_file(options.rfile)
            except exceptions.FlowReadException as v:
                self.add_log("Flow file corrupted.", "error")
                raise DumpError(v)

        if self.options.app:
            self.start_app(self.options.app_host, self.options.app_port)