	def _create_estimator(self, job_type=None):
		if job_type is None:
			with self._selectedFileMutex:
				if self._selectedFile is None:
					return

				if self._selectedFile["sd"]:
					job_type = "sdcard"
				else:
					job_type = "local"

		self._estimator = self._estimator_factory(job_type)