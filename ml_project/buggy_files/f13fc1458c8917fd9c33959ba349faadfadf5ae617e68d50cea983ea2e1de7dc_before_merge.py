		def _readable_name(n):
			if not isinstance(n, str) and not isinstance(n, unicode):
				raise TypeError("expected string, got " + type(n))
			if n == n.upper():
				n.lstrip('_')
			return n.replace('__', '/').replace('_', ' ')