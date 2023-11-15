    def stderr_file(self):
        """Filename to save kernel stderr output."""
        json_file = osp.basename(self.connection_file)
        stderr_file = json_file.split('json')[0] + 'stderr'
        stderr_file = osp.join(TEMPDIR, stderr_file)
        return stderr_file