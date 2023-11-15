	def append(self, tag, attrib=None, text=None):
		attrib = attrib.copy() if attrib is not None else None
		if tag in BLOCK_LEVEL:
			if text and not text.endswith('\n'):
				text += '\n'

		# FIXME hack for backward compat
		if text and tag in (HEADING, LISTITEM):
			text = text.strip('\n')

		self._b.start(tag, attrib)
		if text:
			self._b.data(text)
		self._b.end(tag)

		# FIXME hack for backward compat
		if tag == HEADING and not self._parsetree_roundtrip:
			self._b.data('\n')

		self._last_char = None