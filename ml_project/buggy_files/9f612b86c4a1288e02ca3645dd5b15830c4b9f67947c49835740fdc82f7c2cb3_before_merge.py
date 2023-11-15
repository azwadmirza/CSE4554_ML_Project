    def getargv_install_command(self, name, default="", replace=True):
        s = self.getstring(name, default, replace=False)
        if not s:
            # This occurs when factors are used, and a testenv doesnt have
            # a factorised value for install_command, most commonly occurring
            # if setting platform is also used.
            # An empty value causes error install_command must contain '{packages}'.
            s = default

        if "{packages}" in s:
            s = s.replace("{packages}", r"\{packages\}")
        if "{opts}" in s:
            s = s.replace("{opts}", r"\{opts\}")

        return _ArgvlistReader.getargvlist(self, s, replace=replace)[0]