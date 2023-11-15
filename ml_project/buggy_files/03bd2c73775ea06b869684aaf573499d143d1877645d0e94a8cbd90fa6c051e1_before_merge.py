    def _scp_recv(self, host, remote_file, local_file, recurse=False):
        self._make_ssh_client(host)
        return self._handle_greenlet_exc(
            self.host_clients[host].scp_recv, host,
            remote_file, local_file, recurse=recurse)