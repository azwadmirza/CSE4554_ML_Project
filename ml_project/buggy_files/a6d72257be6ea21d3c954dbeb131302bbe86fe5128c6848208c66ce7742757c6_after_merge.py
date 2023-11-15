    def __del__(self):
        self.primary_buffer = None
        self._native_dsound.Release()