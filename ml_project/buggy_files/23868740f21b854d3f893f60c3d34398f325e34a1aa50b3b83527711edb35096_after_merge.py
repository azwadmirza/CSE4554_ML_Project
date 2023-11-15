    def delete(self):
        if self._native_buffer is not None:
            self._native_buffer.Stop()
            self._native_buffer.Release()
            self._native_buffer = None
            if self._native_buffer3d is not None:
                self._native_buffer3d.Release()
                self._native_buffer3d = None