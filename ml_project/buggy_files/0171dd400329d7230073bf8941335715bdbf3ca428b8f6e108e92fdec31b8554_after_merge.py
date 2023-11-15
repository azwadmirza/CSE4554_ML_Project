    def __init__(self, training_job_name, metric_names=None, sagemaker_session=None):
        """Initialize a ``TrainingJobAnalytics`` instance.

        Args:
            training_job_name (str): name of the TrainingJob to analyze.
            metric_names (list, optional): string names of all the metrics to collect for this training job.
                If not specified, then it will use all metric names configured for this job.
            sagemaker_session (sagemaker.session.Session): Session object which manages interactions with
                Amazon SageMaker APIs and any other AWS services needed. If not specified, one is specified
                using the default AWS configuration chain.
        """
        sagemaker_session = sagemaker_session or Session()
        self._sage_client = sagemaker_session.sagemaker_client
        self._cloudwatch = sagemaker_session.boto_session.client('cloudwatch')
        self._training_job_name = training_job_name
        if metric_names:
            self._metric_names = metric_names
        else:
            self._metric_names = self._metric_names_for_training_job()
        self.clear_cache()