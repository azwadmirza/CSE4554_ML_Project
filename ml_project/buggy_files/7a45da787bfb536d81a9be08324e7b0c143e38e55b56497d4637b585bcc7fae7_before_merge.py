	def start_print(self, pos=None, user=None, *args, **kwargs):
		"""
		 Starts the currently loaded print job.
		 Only starts if the printer is connected and operational, not currently printing and a printjob is loaded
		"""
		if self._comm is None or not self._comm.isOperational() or self._comm.isPrinting():
			return
		with self._selectedFileMutex:
			if self._selectedFile is None:
				return

		# we are happy if the average of the estimates stays within 60s of the prior one
		threshold = settings().getFloat(["estimation", "printTime", "stableThreshold"])
		rolling_window = None
		countdown = None

		with self._selectedFileMutex:
			if self._selectedFile["sd"]:
				# we are interesting in a rolling window of roughly the last 15s, so the number of entries has to be derived
				# by that divided by the sd status polling interval
				rolling_window = 15 / settings().get(["serial", "timeout", "sdStatus"])

				# we are happy when one rolling window has been stable
				countdown = rolling_window
		self._timeEstimationData = TimeEstimationHelper(rolling_window=rolling_window,
		                                                threshold=threshold,
		                                                countdown=countdown)

		self._fileManager.delete_recovery_data()

		self._lastProgressReport = None
		self._updateProgressData()
		self._setCurrentZ(None)
		self._setPrintingUser(user)
		self._comm.startPrint(pos=pos,
		                      tags=kwargs.get("tags", set()) | {"trigger:printer.start_print"})