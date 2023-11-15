    def delete(self):
        assert _debug("Delete interface.DirectSoundListener")
        if self._native_listener:
            self._native_listener.Release()
            self._native_listener = None