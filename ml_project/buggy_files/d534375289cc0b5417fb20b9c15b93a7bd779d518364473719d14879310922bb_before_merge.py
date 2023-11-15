    def generate_names(self):
        impls = OrderedDict()
        if self.implementation:
            # first consider implementation as it is
            impls[self.implementation] = False
            if fs_is_case_sensitive():
                # for case sensitive file systems consider lower and upper case versions too
                # trivia: MacBooks and all pre 2018 Windows-es were case insensitive by default
                impls[self.implementation.lower()] = False
                impls[self.implementation.upper()] = False
        impls["python"] = True  # finally consider python as alias, implementation must match now
        version = self.major, self.minor, self.micro
        try:
            version = version[: version.index(None)]
        except ValueError:
            pass
        for impl, match in impls.items():
            for at in range(len(version), -1, -1):
                cur_ver = version[0:at]
                spec = "{}{}".format(impl, ".".join(str(i) for i in cur_ver))
                yield spec, match