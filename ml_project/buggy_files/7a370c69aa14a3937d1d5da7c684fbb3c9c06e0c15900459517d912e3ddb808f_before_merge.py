    def _connect_tunnel(self, **paramiko_kwargs):
        """Connects to SSH server via an intermediate SSH tunnel server.
        client (me) -> tunnel (ssh server to proxy through) ->
        ``self.host`` (ssh server to run command)

        :rtype: :py:class:`paramiko.SSHClient` Client to remote SSH destination
        via intermediate SSH tunnel server.
        """
        self.proxy_client = paramiko.SSHClient()
        self.proxy_client.set_missing_host_key_policy(
            paramiko.MissingHostKeyPolicy())
        self._connect(self.proxy_client, self.proxy_host, self.proxy_port,
                      user=self.proxy_user, password=self.proxy_password,
                      pkey=self.proxy_pkey, **paramiko_kwargs)
        logger.info("Connecting via SSH proxy %s:%s -> %s:%s", self.proxy_host,
                    self.proxy_port, self.host, self.port,)
        try:
            proxy_channel = self.proxy_client.get_transport().open_channel(
                'direct-tcpip', (self.host, self.port,), ('127.0.0.1', 0),
                timeout=self.timeout)
            sleep(0)
            return self._connect(self.client, self.host, self.port,
                                 sock=proxy_channel,
                                 **paramiko_kwargs)
        except (ChannelException, paramiko.SSHException) as ex:
            error_type = ex.args[1] if len(ex.args) > 1 else ex.args[0]
            raise ConnectionErrorException(
                "Error connecting to host '%s:%s' - %s",
                self.host, self.port, str(error_type))