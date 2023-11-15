    def sftp_get(self, sftp, remote_file, local_file):
        with self._sftp_openfh(
                sftp.open, remote_file,
                LIBSSH2_FXF_READ, LIBSSH2_SFTP_S_IRUSR) as remote_fh:
            try:
                self._sftp_get(remote_fh, local_file)
                # Running SFTP in a thread requires a new session
                # as session handles or any handles created by a session
                # cannot be used simultaneously in multiple threads.
                # THREAD_POOL.apply(
                #     sftp_get, args=(self.session, remote_fh, local_file))
            except SFTPProtocolError as ex:
                msg = "Error reading from remote file %s - %s"
                logger.error(msg, remote_file, ex)
                raise SFTPIOError(msg, remote_file, ex)