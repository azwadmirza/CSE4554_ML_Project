    def _sftp_put(self, remote_fh, local_file):
        with open(local_file, 'rb') as local_fh:
            for data in local_fh:
                self._eagain(remote_fh.write, data)