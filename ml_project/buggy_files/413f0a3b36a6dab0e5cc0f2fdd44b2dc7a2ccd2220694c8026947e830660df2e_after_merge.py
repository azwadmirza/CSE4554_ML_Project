    def delete(self):
        if self._native_listener:
            self._native_listener.Release()
            self._native_listener = None