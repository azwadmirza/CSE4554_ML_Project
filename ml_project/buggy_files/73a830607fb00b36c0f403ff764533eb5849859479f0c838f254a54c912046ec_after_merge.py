    def set_cwd(self, dirname):
        """Set shell current working directory."""
        if os.name == 'nt':
            # Use normpath instead of replacing '\' with '\\'
            # See spyder-ide/spyder#10785
            dirname = osp.normpath(dirname)

        if self.ipyclient.hostname is None:
            self.call_kernel(interrupt=True).set_cwd(dirname)
            self._cwd = dirname