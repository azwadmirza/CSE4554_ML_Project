	def reset(self, interval=None):
		with self._mutex:
			if interval:
				self.interval = interval

			self.is_reset = True
			self._event.set()
			self._event.clear()

		if callable(self.on_reset):
			self.on_reset()