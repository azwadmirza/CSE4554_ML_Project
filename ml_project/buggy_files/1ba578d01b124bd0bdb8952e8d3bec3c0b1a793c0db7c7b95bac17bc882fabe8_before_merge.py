    def _scp_send(self, host, local_file, remote_file, recurse=False):
        self._make_ssh_client(host)
        return self._handle_greenlet_exc(
            self.host_clients[host].scp_send, host,
            local_file, remote_file, recurse=recurse)