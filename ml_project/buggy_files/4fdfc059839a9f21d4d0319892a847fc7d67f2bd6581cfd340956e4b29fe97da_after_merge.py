    def retrieve_job(self, job_id):
        """Attempt to get the specified job by job_id

        Args:
            job_id (str): the job id of the job to retrieve

        Returns:
            IBMQJob: class instance

        Raises:
            IBMQBackendError: if retrieval failed
            DeprecatedFormatJobError: if the job retrieved has a format pre 0.7
        """
        try:
            job_info = self._api.get_status_job(job_id)
            if 'error' in job_info:
                raise IBMQBackendError('Failed to get job "{}": {}'
                                       .format(job_id, job_info['error']))
        except ApiError as ex:
            raise IBMQBackendError('Failed to get job "{}":{}'
                                   .format(job_id, str(ex)))
        job_class = _job_class_from_job_response(job_info)
        if job_class is IBMQJobPreQobj:
            raise DeprecatedFormatJobError('The result of job {} is in an old and no '
                                           'longer supported format, please resend the '
                                           'job with Qiskit 0.7'.format(job_id))

        is_device = not bool(self.configuration().simulator)
        job = job_class(self, job_info.get('id'), self._api, is_device,
                        creation_date=job_info.get('creationDate'),
                        api_status=job_info.get('status'))
        return job