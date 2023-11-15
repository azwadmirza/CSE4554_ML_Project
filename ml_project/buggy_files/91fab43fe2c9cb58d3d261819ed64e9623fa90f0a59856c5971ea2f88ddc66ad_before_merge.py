	def _gcode_M110_sending(self, cmd, cmd_type=None):
		newLineNumber = None
		match = regexes_parameters["intN"].search(cmd)
		if match:
			try:
				newLineNumber = int(match.group("value"))
			except:
				pass
		else:
			newLineNumber = 0

		with self._line_mutex:
			# send M110 command with new line number
			self._currentLine = newLineNumber

			# after a reset of the line number we have no way to determine what line exactly the printer now wants
			self._lastLines.clear()
		self._resendDelta = None