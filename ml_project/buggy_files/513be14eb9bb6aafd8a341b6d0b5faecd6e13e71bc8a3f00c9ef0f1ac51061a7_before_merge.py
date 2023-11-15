    def _copy_file(self, host, local_file, remote_file, recurse=False):
        """Make sftp client, copy file"""
        try:
            self._make_ssh_client(host)
            return self.host_clients[host].copy_file(local_file, remote_file,
                                                     recurse=recurse)
        except Exception as ex:
            ex.host = host
            raise ex