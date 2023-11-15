    def set_cwd(self, dirname):
        """Set shell current working directory."""
        # Replace single for double backslashes on Windows
        if os.name == 'nt':
            dirname = dirname.replace(u"\\", u"\\\\")

        if self.ipyclient.hostname is None:
            self.call_kernel(interrupt=True).set_cwd(dirname)
            self._cwd = dirname