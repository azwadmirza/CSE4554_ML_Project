    def _proc_cred(self):
        return cext.proc_cred(self.pid, self._procfs_path)