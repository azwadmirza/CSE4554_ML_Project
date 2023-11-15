	def __init__(self, delimiter=b'\n', *args, **kwargs):
		self._delimiter = delimiter
		sarge.Capture.__init__(self, *args, **kwargs)