    def _copy_remote_file(self, host_i, host, remote_file, local_file, recurse,
                          **kwargs):
        """Make sftp client, copy file to local"""
        try:
            self._make_ssh_client(host_i, host)
            return self._host_clients[(host_i, host)].copy_remote_file(
                remote_file, local_file, recurse=recurse, **kwargs)
        except Exception as ex:
            ex.host = host
            raise ex