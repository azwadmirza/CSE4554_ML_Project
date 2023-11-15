    def update_key(self):
        args = tuple(getattr(self, k, None) for k in self._keys_)
        if self.state is None:
            args += (np.random.random(),)
        self._key = tokenize(type(self), *args)