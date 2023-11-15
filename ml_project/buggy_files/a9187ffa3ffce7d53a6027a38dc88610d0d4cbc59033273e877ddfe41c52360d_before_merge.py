    def update_key(self):
        args = tuple(getattr(self, k, None) for k in self.__slots__)
        if self.state is None:
            args += (np.random.random(),)
        self._key = tokenize(type(self), *args)