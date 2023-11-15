    def _scp_send(self, host_i, host, local_file, remote_file, recurse=False):
        self._make_ssh_client(host_i, host)
        return self._handle_greenlet_exc(
            self._host_clients[(host_i, host)].scp_send, host,
            local_file, remote_file, recurse=recurse)