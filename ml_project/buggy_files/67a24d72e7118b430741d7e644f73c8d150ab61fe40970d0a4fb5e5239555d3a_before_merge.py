    def _connect_proxy(self, proxy_host, proxy_port, proxy_pkey,
                       user=None, password=None,
                       num_retries=DEFAULT_RETRIES,
                       retry_delay=RETRY_DELAY,
                       allow_agent=True, timeout=None,
                       forward_ssh_agent=False,
                       keepalive_seconds=60,
                       identity_auth=True):
        assert isinstance(self.port, int)
        try:
            self._proxy_client = SSHClient(
                proxy_host, port=proxy_port, pkey=proxy_pkey,
                num_retries=num_retries, user=user, password=password,
                retry_delay=retry_delay, allow_agent=allow_agent,
                timeout=timeout, forward_ssh_agent=forward_ssh_agent,
                identity_auth=identity_auth,
                keepalive_seconds=keepalive_seconds,
                _auth_thread_pool=False)
        except Exception as ex:
            msg = "Proxy authentication failed. " \
                  "Exception from tunnel client: %s"
            logger.error(msg, ex)
            raise ProxyError(msg, ex)
        if not FORWARDER.started.is_set():
            FORWARDER.start()
            FORWARDER.started.wait()
        FORWARDER.in_q.put((self._proxy_client, self.host, self.port))
        proxy_local_port = FORWARDER.out_q.get()
        return proxy_local_port