    def getbool(self, name, default=None, replace=True):
        s = self.getstring(name, default, replace=replace)
        if not s:
            s = default
        if s is None:
            raise KeyError("no config value [%s] %s found" % (
                           self.section_name, name))

        if not isinstance(s, bool):
            if s.lower() == "true":
                s = True
            elif s.lower() == "false":
                s = False
            else:
                raise tox.exception.ConfigError(
                    "boolean value %r needs to be 'True' or 'False'")
        return s