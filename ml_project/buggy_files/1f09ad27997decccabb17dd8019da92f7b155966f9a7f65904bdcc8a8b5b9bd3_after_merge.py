    def describe(self):
        """Prints out a response from the DescribeProcessingJob API call."""
        return self.sagemaker_session.describe_processing_job(self.job_name)