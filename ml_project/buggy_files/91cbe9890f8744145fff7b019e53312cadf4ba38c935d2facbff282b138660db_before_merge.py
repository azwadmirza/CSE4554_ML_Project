    def create_stream(self):
        handle = drvapi.cu_stream()
        driver.cuStreamCreate(byref(handle), 0)
        return Stream(weakref.proxy(self), handle,
                      _stream_finalizer(self.allocations, handle))