    def _connect_to_v1(self):
        line = self._read_protocol_line()
        match = re.match('^SNIPPET SERVING, PORT ([0-9]+)$', line)
        if not match:
            raise jsonrpc_client_base.AppStartError(line)
        self.device_port = int(match.group(1))

        # Forward the device port to a new host port, and connect to that port
        self.host_port = utils.get_available_host_port()
        self._adb.forward(
            ['tcp:%d' % self.host_port,
             'tcp:%d' % self.device_port])
        self.connect()