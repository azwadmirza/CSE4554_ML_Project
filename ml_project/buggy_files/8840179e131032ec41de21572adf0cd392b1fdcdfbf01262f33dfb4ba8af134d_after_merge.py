    def __init__(self, shape, strides, dtype, stream=0, writeback=None,
                 gpu_data=None):
        """
        Args
        ----

        shape
            array shape.
        strides
            array strides.
        dtype
            data type as np.dtype.
        stream
            cuda stream.
        writeback
            Deprecated.
        gpu_data
            user provided device memory for the ndarray data buffer
        """
        if isinstance(shape, (int, long)):
            shape = (shape,)
        if isinstance(strides, (int, long)):
            strides = (strides,)
        self.ndim = len(shape)
        if len(strides) != self.ndim:
            raise ValueError('strides not match ndim')
        self._dummy = dummyarray.Array.from_desc(0, shape, strides,
                                                 dtype.itemsize)
        self.shape = tuple(shape)
        self.strides = tuple(strides)
        self.dtype = np.dtype(dtype)
        self.size = int(np.prod(self.shape))
        # prepare gpu memory
        if self.size > 0:
            if gpu_data is None:
                self.alloc_size = _driver.memory_size_from_info(self.shape,
                                                                self.strides,
                                                                self.dtype.itemsize)
                gpu_data = devices.get_context().memalloc(self.alloc_size)
            else:
                self.alloc_size = _driver.device_memory_size(gpu_data)
        else:
            # Make NULL pointer for empty allocation
            gpu_data = _driver.MemoryPointer(context=devices.get_context(),
                                             pointer=c_void_p(0), size=0)
            self.alloc_size = 0

        self.gpu_data = gpu_data

        self.__writeback = writeback    # should deprecate the use of this
        self.stream = 0