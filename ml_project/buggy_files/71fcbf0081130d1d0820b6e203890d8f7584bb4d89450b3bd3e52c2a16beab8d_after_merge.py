    def copy_to_host(self, ary=None, stream=0):
        """Copy ``self`` to ``ary`` or create a new Numpy ndarray
        if ``ary`` is ``None``.

        If a CUDA ``stream`` is given, then the transfer will be made
        asynchronously as part as the given stream.  Otherwise, the transfer is
        synchronous: the function returns after the copy is finished.

        Always returns the host array.

        Example::

            import numpy as np
            from numba import cuda

            arr = np.arange(1000)
            d_arr = cuda.to_device(arr)

            my_kernel[100, 100](d_arr)

            result_array = d_arr.copy_to_host()
        """
        if any(s < 0 for s in self.strides):
            msg = 'D->H copy not implemented for negative strides: {}'
            raise NotImplementedError(msg.format(self.strides))
        assert self.alloc_size >= 0, "Negative memory size"
        stream = self._default_stream(stream)
        if ary is None:
            hostary = np.empty(shape=self.alloc_size, dtype=np.byte)
        else:
            check_array_compatibility(self, ary)
            hostary = ary

        if self.alloc_size != 0:
            _driver.device_to_host(hostary, self, self.alloc_size, stream=stream)

        if ary is None:
            if self.size == 0:
                hostary = np.ndarray(shape=self.shape, dtype=self.dtype,
                                     buffer=hostary)
            else:
                hostary = np.ndarray(shape=self.shape, dtype=self.dtype,
                                     strides=self.strides, buffer=hostary)
        return hostary