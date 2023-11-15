    def verbosity(self):
        if not self.pretty:
            return 999
        return self._verbosity