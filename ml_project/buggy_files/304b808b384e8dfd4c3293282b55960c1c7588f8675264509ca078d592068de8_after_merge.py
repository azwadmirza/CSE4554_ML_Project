    def decode(self):
        """
        Decodes the result of the job.
        :return: Depends on the type of job. A JSON object.
        """
        return self.result['result']