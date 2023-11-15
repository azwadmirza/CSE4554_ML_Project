	def _create_estimator(self, job_type):
		self._estimator = self._estimator_factory(job_type)