    def start_app_and_connect(self):
        """Overrides superclass. Launches a snippet app and connects to it."""
        self._check_app_installed()

        # Try launching the app with the v1 protocol. If that fails, fall back
        # to v0 for compatibility. Use info here so people know exactly what's
        # happening here, which is helpful since they need to create their own
        # instrumentations and manifest.
        self.log.info('Launching snippet apk %s with protocol v1',
                      self.package)
        cmd = _LAUNCH_CMD_V1 % self.package
        start_time = time.time()
        self._proc = self._do_start_app(cmd)

        # "Instrumentation crashed" could be due to several reasons, eg
        # exception thrown during startup or just a launch protocol 0 snippet
        # dying because it needs the port flag. Sadly we have no way to tell so
        # just warn and retry as v0.
        # TODO(adorokhine): delete this in Mobly 1.6 when snippet v0 support is
        # removed.
        line = self._read_protocol_line()
        if line in ('INSTRUMENTATION_RESULT: shortMsg=Process crashed.',
                    'INSTRUMENTATION_RESULT: shortMsg='
                    'java.lang.IllegalArgumentException'):
            self.log.warning('Snippet %s crashed on startup. This might be an '
                             'actual error or a snippet using deprecated v0 '
                             'start protocol. Retrying as a v0 snippet.',
                             self.package)
            self.host_port = utils.get_available_host_port()
            # Reuse the host port as the device port in v0 snippet. This isn't
            # safe in general, but the protocol is deprecated.
            cmd = _LAUNCH_CMD_V0 % (self.host_port, self.package)
            self._proc = self._do_start_app(cmd)
            self._connect_to_v0()
        else:
            # Check protocol version and get the device port
            match = re.match('^SNIPPET START, PROTOCOL ([0-9]+) ([0-9]+)$',
                             line)
            if not match or match.group(1) != '1':
                raise ProtocolVersionError(line)
            self._connect_to_v1()
        self.log.debug('Snippet %s started after %.1fs on host port %s',
                       self.package, time.time() - start_time, self.host_port)