    def _proc_cred(self):
        @wrap_exceptions
        def proc_cred(self):
            return cext.proc_cred(self.pid, self._procfs_path)
        return proc_cred(self)