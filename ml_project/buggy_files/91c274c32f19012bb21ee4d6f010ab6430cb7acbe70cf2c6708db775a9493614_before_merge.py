    def decref(self, *keys):
        if hasattr(self._sess, 'decref'):
            self._sess.decref(*keys)