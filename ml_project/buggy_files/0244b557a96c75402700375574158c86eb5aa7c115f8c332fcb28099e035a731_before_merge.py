	def start(self, tag, attrib=None):
		self._b.start(tag, attrib)
		self.stack.append(tag)
		if tag in BLOCK_LEVEL:
			self._last_char = None