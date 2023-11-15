	def on_print_resumed(self, event, payload):
		"""
		Override this to perform additional actions upon the pausing of a print job.
		"""
		if not self._in_timelapse:
			self.start_timelapse(payload["file"])