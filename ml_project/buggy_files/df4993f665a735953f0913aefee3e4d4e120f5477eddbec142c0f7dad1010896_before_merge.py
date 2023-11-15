    def view(self, start, stop=None):
        base = self.device_pointer.value + start
        if stop is None:
            size = self.size - start
        else:
            size = stop - start
        assert size > 0, "zero or negative memory size"
        pointer = drvapi.cu_device_ptr(base)
        view = MemoryPointer(self.context, pointer, size, owner=self.owner)
        return OwnedPointer(weakref.proxy(self.owner), view)