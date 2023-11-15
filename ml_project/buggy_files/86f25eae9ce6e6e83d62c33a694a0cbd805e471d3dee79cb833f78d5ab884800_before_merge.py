    def _sftp_openfh(self, open_func, remote_file, *args):
        try:
            fh = open_func(remote_file, *args)
        except Exception as ex:
            raise SFTPError(ex)
        while fh == LIBSSH2_ERROR_EAGAIN:
            self.poll(timeout=0.1)
            try:
                fh = open_func(remote_file, *args)
            except Exception as ex:
                raise SFTPError(ex)
        return fh