	def start(self, tag, attrib=None):
		attrib = attrib.copy() if attrib is not None else None
		self._b.start(tag, attrib)
		self.stack.append(tag)
		if tag in BLOCK_LEVEL:
			self._last_char = None