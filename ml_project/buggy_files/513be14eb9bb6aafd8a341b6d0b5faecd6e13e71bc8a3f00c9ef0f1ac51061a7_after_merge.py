    def _copy_file(self, host_i, host, local_file, remote_file, recurse=False):
        """Make sftp client, copy file"""
        try:
            self._make_ssh_client(host_i, host)
            return self._host_clients[(host_i, host)].copy_file(
                local_file, remote_file, recurse=recurse)
        except Exception as ex:
            ex.host = host
            raise ex