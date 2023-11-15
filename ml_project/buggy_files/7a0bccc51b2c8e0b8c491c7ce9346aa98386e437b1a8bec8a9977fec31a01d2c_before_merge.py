    def __contains__(self, key):
        if not self._finished:
            raise RuntimeError("Still collecting draws for fit.")
        return key in self.param_names