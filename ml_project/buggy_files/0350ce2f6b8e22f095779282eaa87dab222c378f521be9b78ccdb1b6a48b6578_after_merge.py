    def _make_sftp(self):
        """Make SFTP client from open transport"""
        try:
            sftp = self._eagain(self.session.sftp_init)
        except Exception as ex:
            raise SFTPError(ex)
        return sftp