    def set(self, key, value, **retry_policy):
        return self.ensure(self._set, (key, value), **retry_policy)