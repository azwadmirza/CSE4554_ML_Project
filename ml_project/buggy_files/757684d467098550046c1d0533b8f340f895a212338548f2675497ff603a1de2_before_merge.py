    def pull_file(self, remote_source, local_dir):
        ''' Transport file on the remote side to a local directory

        Args:
            - remote_source (string): remote_source
            - local_dir (string): Local directory to copy to


        Returns:
            - str: Local path to file

        Raises:
            - FileExists : Name collision at local directory.
            - FileCopyException : FileCopy failed.
        '''

        local_dest = local_dir + '/' + os.path.basename(remote_source)

        try:
            os.makedirs(local_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.exception("Failed to create local_dir: {0}".format(local_dir))
                raise BadScriptPath(e, self.hostname)

        # Easier to check this than to waste time trying to pull file and
        # realize there's a problem.
        if os.path.exists(local_dest):
            logger.exception("Remote file copy will overwrite a local file:{0}".format(local_dest))
            raise FileExists(None, self.hostname, filename=local_dest)

        try:
            self._valid_sftp_client().get(remote_source, local_dest)
        except Exception as e:
            logger.exception("File pull failed")
            raise FileCopyException(e, self.hostname)

        return local_dest