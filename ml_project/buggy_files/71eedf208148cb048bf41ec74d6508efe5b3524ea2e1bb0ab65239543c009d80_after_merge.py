    def _make_ssh_client(self, host_i, host):
        auth_thread_pool = True
        if self.proxy_host is not None and self._tunnel is None:
            self._start_tunnel_thread()
        logger.debug("Make client request for host %s, host in clients: %s",
                     host, host in self.host_clients)
        with self._clients_lock:
            if (host_i, host) not in self._host_clients \
               or self._host_clients[(host_i, host)] is None:
                _user, _port, _password, _pkey = self._get_host_config_values(
                    host)
                proxy_host = None if self.proxy_host is None else '127.0.0.1'
                if proxy_host is not None:
                    auth_thread_pool = False
                    _wait = 0.0
                    max_wait = self.timeout if self.timeout is not None else 60
                    with self._tunnel_lock:
                        self._tunnel_in_q.append((host, _port))
                    while True:
                        if _wait >= max_wait:
                            raise Timeout("Timed out waiting on tunnel to "
                                          "open listening port")
                        try:
                            _port = self._tunnel_out_q.pop()
                        except IndexError:
                            logger.debug(
                                "Waiting on tunnel to open listening port")
                            sleep(.5)
                            _wait += .5
                        else:
                            break
                _client = SSHClient(
                    host, user=_user, password=_password, port=_port,
                    pkey=_pkey, num_retries=self.num_retries,
                    timeout=self.timeout,
                    allow_agent=self.allow_agent, retry_delay=self.retry_delay,
                    proxy_host=proxy_host, _auth_thread_pool=auth_thread_pool,
                    forward_ssh_agent=self.forward_ssh_agent,
                    keepalive_seconds=self.keepalive_seconds)
                self.host_clients[host] = _client
                self._host_clients[(host_i, host)] = _client