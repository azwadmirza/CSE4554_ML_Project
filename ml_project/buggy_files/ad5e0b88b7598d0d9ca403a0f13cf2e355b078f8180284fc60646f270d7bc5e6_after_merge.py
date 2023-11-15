	def _on_external_reset(self):
		# hold queue processing, clear queues and acknowledgements, reset line number and last lines
		with self._send_queue.blocked():
			self._clear_to_send.reset()
			with self._command_queue.blocked():
				self._command_queue.clear()
			self._send_queue.clear()

			with self._line_mutex:
				self._currentLine = 0
				self._lastLines.clear()

		self.sayHello(tags={"trigger:comm.on_external_reset"})
		self.resetLineNumbers(tags={"trigger:comm.on_external_reset"})

		if self._temperature_autoreporting:
			self._set_autoreport_temperature_interval()
		if self._sdstatus_autoreporting:
			self._set_autoreport_sdstatus_interval()
		if self._busy_protocol_support:
			self._set_busy_protocol_interval()