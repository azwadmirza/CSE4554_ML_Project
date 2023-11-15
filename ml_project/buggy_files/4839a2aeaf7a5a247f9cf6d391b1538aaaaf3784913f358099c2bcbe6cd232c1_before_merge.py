    def status(self, job_ids):
        ''' Get the status of a list of jobs identified by the job identifiers
        returned from the submit request.

        Args:
             - job_ids (list) : A list of job identifiers

        Returns:
             - A list of JobStatus objects corresponding to each job_id in the job_ids list.

        Raises:
             - ExecutionProviderException or its subclasses

        '''
        statuses = []
        for job_id in job_ids:
            instance = self.client.instances().get(instance=job_id, project=self.project_id, zone=self.zone).execute()
            self.resources[job_id]['status'] = JobStatus(translate_table[instance['status']])
            statuses.append(translate_table[instance['status']])
        return statuses