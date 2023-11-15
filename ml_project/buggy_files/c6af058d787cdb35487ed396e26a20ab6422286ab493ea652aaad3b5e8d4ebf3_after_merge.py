    def stderr_file(self):
        """Filename to save kernel stderr output."""
        if self.connection_file is not None:
            stderr_file = self.kernel_id + '.stderr'
            stderr_file = osp.join(TEMPDIR, stderr_file)
            return stderr_file