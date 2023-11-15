    def __del__(self):
        assert _debug("Delete DirectSoundAudioPlayer")
        # We decrease the IDirectSound refcount
        self.driver._ds_driver._native_dsound.Release()