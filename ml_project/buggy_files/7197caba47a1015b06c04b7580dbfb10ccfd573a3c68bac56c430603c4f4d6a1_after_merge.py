    def exe(self):
        # Dual implementation, see:
        # https://github.com/giampaolo/psutil/pull/1413
        if not IS_WIN_XP:
            exe = cext.proc_exe(self.pid)
        else:
            if self.pid in (0, 4):
                # https://github.com/giampaolo/psutil/issues/414
                # https://github.com/giampaolo/psutil/issues/528
                raise AccessDenied(self.pid, self._name)
            exe = cext.proc_exe(self.pid)
            exe = convert_dos_path(exe)
        return py2_strencode(exe)