	def on_print_started(self, event, payload):
		"""
		Override this to perform additional actions upon start of a print job.
		"""
		self.start_timelapse(payload["name"])