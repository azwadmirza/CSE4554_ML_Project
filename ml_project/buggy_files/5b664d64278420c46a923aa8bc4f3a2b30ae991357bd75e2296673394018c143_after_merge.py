    def training_job_analytics(self):
        """Return a ``TrainingJobAnalytics`` object for the current training job.
        """
        if self._current_job_name is None:
            raise ValueError('Estimator is not associated with a TrainingJob')
        return TrainingJobAnalytics(self._current_job_name, sagemaker_session=self.sagemaker_session)