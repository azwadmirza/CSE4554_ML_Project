    def view(self, start, stop=None):
        if stop is None:
            size = self.size - start
        else:
            size = stop - start

        # Handle NULL/empty memory buffer
        if self.device_pointer.value is None:
            if size != 0:
                raise RuntimeError("non-empty slice into empty slice")
            view = self      # new view is just a reference to self
        # Handle normal case
        else:
            base = self.device_pointer.value + start
            if size < 0:
                raise RuntimeError('size cannot be negative')
            pointer = drvapi.cu_device_ptr(base)
            view = MemoryPointer(self.context, pointer, size, owner=self.owner)
        return OwnedPointer(weakref.proxy(self.owner), view)