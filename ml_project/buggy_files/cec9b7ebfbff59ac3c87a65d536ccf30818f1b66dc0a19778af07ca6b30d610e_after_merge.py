    def _start_tunnel(self, host):
        if host in self._tunnels:
            return self._tunnels[host]
        tunnel = Tunnel(
            self.proxy_host, host, self.port, user=self.proxy_user,
            password=self.proxy_password, port=self.proxy_port,
            pkey=self.proxy_pkey, num_retries=self.num_retries,
            timeout=self.timeout, retry_delay=self.retry_delay,
            allow_agent=self.allow_agent)
        tunnel.daemon = True
        tunnel.start()
        while not tunnel.tunnel_open.is_set():
            logger.debug("Waiting for tunnel to become active")
            sleep(.1)
            if not tunnel.is_alive():
                msg = "Proxy authentication failed. " \
                      "Exception from tunnel client: %s"
                logger.error(msg, tunnel.exception)
                raise ProxyError(msg, tunnel.exception)
        self._tunnels[host] = tunnel
        return tunnel