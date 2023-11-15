    def __call__(self, x):
        if not self.variational_params_initialized.item():
            self.initialize_variational_dist()
            self.variational_params_initialized.fill_(1)
        if self.training:
            if hasattr(self, "_memoize_cache"):
                delattr(self, "_memoize_cache")
                self._memoize_cache = dict()

        return super(VariationalStrategy, self).__call__(x)