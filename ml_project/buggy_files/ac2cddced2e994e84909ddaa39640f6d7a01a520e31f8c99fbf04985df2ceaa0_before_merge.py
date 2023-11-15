	def __call__(self, device):
		assert not hasattr(self, '_value')
		assert self.device_kind is None or device.kind in self.device_kind
		p = device.protocol
		if p == 1.0:
			# HID++ 1.0 devices do not support features
			assert self._rw.kind == RegisterRW.kind
		elif p >= 2.0:
			# HID++ 2.0 devices do not support registers
			assert self._rw.kind == FeatureRW.kind

		o = _copy(self)
		o._value = None
		o._device = device
		return o