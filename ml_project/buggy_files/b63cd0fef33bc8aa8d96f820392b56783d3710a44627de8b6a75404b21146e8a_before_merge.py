    def _make_ssh_client(self, host, **paramiko_kwargs):
        if host not in self.host_clients or self.host_clients[host] is None:
            _user, _port, _password, _pkey = self._get_host_config_values(host)
            self.host_clients[host] = SSHClient(
                host, user=_user, password=_password, port=_port, pkey=_pkey,
                forward_ssh_agent=self.forward_ssh_agent,
                num_retries=self.num_retries, timeout=self.timeout,
                proxy_host=self.proxy_host, proxy_port=self.proxy_port,
                proxy_user=self.proxy_user, proxy_password=self.proxy_password,
                proxy_pkey=self.proxy_pkey, allow_agent=self.allow_agent,
                agent=self.agent, channel_timeout=self.channel_timeout,
                **paramiko_kwargs)