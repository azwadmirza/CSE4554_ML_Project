	def _readline(self):
		if self._serial is None:
			return None

		try:
			ret = self._serial.readline()
		except Exception as ex:
			if not self._connection_closing:
				self._logger.exception("Unexpected error while reading from serial port")
				self._log("Unexpected error while reading serial port, please consult octoprint.log for details: %s" % (get_exception_string()))
				if isinstance(ex, serial.SerialException):
					self._dual_log("Please see https://faq.octoprint.org/serialerror for possible reasons of this.",
					               level=logging.ERROR)
				self._errorValue = get_exception_string()
				self.close(is_error=True)
			return None

		try:
			ret = ret.decode('utf-8')
		except UnicodeDecodeError:
			ret = ret.decode('latin1')

		self._log(u"Recv: {}".format(ret))

		for name, hook in self._received_message_hooks.items():
			try:
				ret = hook(self, ret)
			except Exception:
				self._logger.exception("Error while processing hook {name}:".format(**locals()),
				                       extra=dict(plugin=name))
			else:
				if ret is None:
					return ""

		return ret