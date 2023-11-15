	def on_comm_state_change(self, state):
		"""
		 Callback method for the comm object, called if the connection state changes.
		"""
		oldState = self._state

		state_string = None
		if self._comm is not None:
			state_string = self._comm.getStateString()

		# forward relevant state changes to gcode manager
		if oldState == comm.MachineCom.STATE_PRINTING:
			if self._selectedFile is not None:
				if state == comm.MachineCom.STATE_CLOSED or state == comm.MachineCom.STATE_ERROR or state == comm.MachineCom.STATE_CLOSED_WITH_ERROR:
					self._fileManager.log_print(FileDestinations.SDCARD if self._selectedFile["sd"] else FileDestinations.LOCAL, self._selectedFile["filename"], time.time(), self._comm.getPrintTime(), False, self._printerProfileManager.get_current_or_default()["id"])
			self._analysisQueue.resume() # printing done, put those cpu cycles to good use
		elif state == comm.MachineCom.STATE_PRINTING:
			self._analysisQueue.pause() # do not analyse files while printing

		if state == comm.MachineCom.STATE_CLOSED or state == comm.MachineCom.STATE_CLOSED_WITH_ERROR:
			if self._comm is not None:
				self._comm = None

			self._setProgressData(completion=0)
			self._setCurrentZ(None)
			self._setJobData(None, None, None)

		self._setState(state, state_string=state_string)