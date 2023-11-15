    def describe(self, print_response=True):
        """Prints out a response from the DescribeProcessingJob API call."""
        describe_response = self.sagemaker_session.describe_processing_job(self.job_name)
        if print_response:
            print(describe_response)
        return describe_response