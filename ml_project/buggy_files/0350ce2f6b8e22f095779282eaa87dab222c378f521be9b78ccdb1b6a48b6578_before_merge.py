    def _make_sftp(self):
        """Make SFTP client from open transport"""
        try:
            sftp = self.session.sftp_init()
        except Exception as ex:
            raise SFTPError(ex)
        while sftp == LIBSSH2_ERROR_EAGAIN:
            self.poll()
            try:
                sftp = self.session.sftp_init()
            except Exception as ex:
                raise SFTPError(ex)
        return sftp