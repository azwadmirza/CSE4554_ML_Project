    def __init__(self, training_job_name, metric_names, sagemaker_session=None):
        """Initialize a ``TrainingJobAnalytics`` instance.

        Args:
            training_job_name (str): name of the TrainingJob to analyze.
            metric_names (list): string names of all the metrics to collect for this training job
            sagemaker_session (sagemaker.session.Session): Session object which manages interactions with
                Amazon SageMaker APIs and any other AWS services needed. If not specified, one is specified
                using the default AWS configuration chain.
        """
        sagemaker_session = sagemaker_session or Session()
        self._sage_client = sagemaker_session.sagemaker_client
        self._cloudwatch = sagemaker_session.boto_session.client('cloudwatch')
        self._training_job_name = training_job_name
        self._metric_names = metric_names
        self.clear_cache()