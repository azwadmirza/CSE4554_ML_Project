    def delete(self):
        assert _debug("Delete interface.DirectSoundBuffer from AudioFormat {}".format(self.audio_format))
        if self._native_buffer is not None:
            self._native_buffer.Stop()
            self._native_buffer.Release()
            self._native_buffer = None
            if self._native_buffer3d is not None:
                self._native_buffer3d.Release()
                self._native_buffer3d = None