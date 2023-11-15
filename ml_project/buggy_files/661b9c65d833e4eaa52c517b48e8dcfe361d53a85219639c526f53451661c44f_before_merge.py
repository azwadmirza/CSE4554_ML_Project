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

			if self._selectedFile["sd"]:
				job_type = "sdcard"
			else:
				job_type = "local"

		self._create_estimator(job_type)
		self._fileManager.delete_recovery_data()

		self._lastProgressReport = None
		self._updateProgressData()
		self._setCurrentZ(None)
		self._comm.startPrint(pos=pos,
		                      tags=kwargs.get("tags", set()) | {"trigger:printer.start_print"})