	def __init__(self, **kwargs):
		def _readable_name(n):
			if not isinstance(n, str) and not isinstance(n, unicode):
				raise TypeError("expected string, got " + type(n))
			if n == n.upper():
				n = n.lstrip('_')
			return n.replace('__', '/').replace('_', ' ')

		values = {k: NamedInt(v, _readable_name(k)) for (k, v) in kwargs.items()}
		self.__dict__ = values
		self._values = sorted(list(values.values()))
		self._indexed = {int(v): v for v in self._values}
		self._fallback = None