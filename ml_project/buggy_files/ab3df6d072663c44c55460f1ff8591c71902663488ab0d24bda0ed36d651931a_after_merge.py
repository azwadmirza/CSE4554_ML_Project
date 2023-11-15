    def __del__(self):
        # We decrease the IDirectSound refcount
        self.driver._ds_driver._native_dsound.Release()