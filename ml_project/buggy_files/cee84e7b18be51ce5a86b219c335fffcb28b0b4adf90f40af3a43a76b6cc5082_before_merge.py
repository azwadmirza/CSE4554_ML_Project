  def __init__(self, aval, device_buffer):
    self.aval = aval
    self.device_buffer = device_buffer
    # TODO(mattjj): make Device hashable
    device = device_buffer.device()
    self._device = device and (type(device), device.id)

    self._npy_value = None
    if not core.skip_checks:
      assert type(aval) is ShapedArray
      npy_value = self._value
      assert npy_value.dtype == aval.dtype and npy_value.shape == aval.shape