    def expand_section(self, configobj, S=None):
        if S is None:
            S = list()
        S.append(configobj)
        for child in configobj.child_objs:
            if child in S:
                continue
            self.expand_section(child, S)
        return S