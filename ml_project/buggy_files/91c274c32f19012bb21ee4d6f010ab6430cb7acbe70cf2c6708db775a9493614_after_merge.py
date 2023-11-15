    def decref(self, *keys):
        self._executed_keys = self._executed_keys.difference(keys)
        if hasattr(self._sess, 'decref'):
            self._sess.decref(*keys)