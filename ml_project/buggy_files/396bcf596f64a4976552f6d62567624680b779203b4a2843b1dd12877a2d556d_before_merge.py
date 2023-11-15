    def _init(self, retries=1):
        self.session = Session()
        if self.timeout:
            # libssh2 timeout is in ms
            self.session.set_timeout(self.timeout * 1000)
        try:
            self.session.handshake(self.sock)
        except Exception as ex:
            while retries < self.num_retries:
                return self._connect_init_retry(retries)
            msg = "Error connecting to host %s:%s - %s"
            logger.error(msg, self.host, self.port, ex)
            if isinstance(ex, SSH2Timeout):
                raise Timeout(msg, self.host, self.port, ex)
            raise
        try:
            self.auth()
        except Exception as ex:
            while retries < self.num_retries:
                return self._connect_init_retry(retries)
            msg = "Authentication error while connecting to %s:%s - %s"
            raise AuthenticationException(msg, self.host, self.port, ex)
        self.session.set_blocking(0)
        if self.keepalive_seconds:
            self.configure_keepalive()
            self._keepalive_greenlet = self.spawn_send_keepalive()