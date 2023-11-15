    def _sftp_openfh(self, open_func, remote_file, *args):
        try:
            fh = self._eagain(open_func, remote_file, *args)
        except Exception as ex:
            raise SFTPError(ex)
        return fh