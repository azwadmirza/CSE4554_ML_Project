    def exe(self):
        # Note: os.path.exists(path) may return False even if the file
        # is there, see:
        # http://stackoverflow.com/questions/3112546/os-path-exists-lies

        # see https://github.com/giampaolo/psutil/issues/414
        # see https://github.com/giampaolo/psutil/issues/528
        if self.pid in (0, 4):
            raise AccessDenied(self.pid, self._name)
        exe = cext.proc_exe(self.pid)
        exe = convert_dos_path(exe)
        return py2_strencode(exe)