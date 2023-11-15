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
        self._tunnels[host] = tunnel
        while not tunnel.tunnel_open.is_set():
            logger.debug("Waiting for tunnel to become active")
            sleep(.1)
            if not tunnel.is_alive():
                msg = "Proxy authentication failed"
                logger.error(msg)
                raise ProxyError(msg)
        return tunnel