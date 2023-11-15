  def __getitem__(self, idx):
    if self._npy_value is None and type(idx) is int:
      ids = self._ids()
      device_buffer = self.device_buffers[ids[idx]]
      aval = ShapedArray(self.aval.shape[1:], self.aval.dtype)
      handler = xla.aval_to_result_handler(aval)
      return handler(device_buffer)
    else:
      return super(ShardedDeviceArray, self).__getitem__(idx)