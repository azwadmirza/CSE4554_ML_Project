    def getargv_install_command(self, name, default="", replace=True):
        s = self.getstring(name, default, replace=False)
        if "{packages}" in s:
            s = s.replace("{packages}", r"\{packages\}")
        if "{opts}" in s:
            s = s.replace("{opts}", r"\{opts\}")

        return _ArgvlistReader.getargvlist(self, s, replace=replace)[0]