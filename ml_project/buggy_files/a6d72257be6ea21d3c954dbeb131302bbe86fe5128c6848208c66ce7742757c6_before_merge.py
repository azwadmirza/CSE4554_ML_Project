    def __del__(self):
        assert _debug("Delete interface.DirectSoundDriver")
        self.primary_buffer = None
        self._native_dsound.Release()