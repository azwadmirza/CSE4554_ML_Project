    def _scp_recv(self, host_i, host, remote_file, local_file, recurse=False):
        self._make_ssh_client(host_i, host)
        return self._handle_greenlet_exc(
            self._host_clients[(host_i, host)].scp_recv, host,
            remote_file, local_file, recurse=recurse)