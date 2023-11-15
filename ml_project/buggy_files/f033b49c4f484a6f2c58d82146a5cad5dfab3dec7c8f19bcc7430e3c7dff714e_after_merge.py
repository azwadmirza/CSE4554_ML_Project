    def verbosity(self):
        if self._verbosity_overriden:
            return self._verbosity
        elif not self.pretty:
            return 999
        return self._verbosity