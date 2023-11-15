    def status(self, job_ids):
        """ Get status of the list of jobs with job_ids

        Parameters
        ----------
        job_ids : list of strings
          List of job id strings

        Returns
        -------
        list of JobStatus objects
        """
        for job_id in job_ids:
            channel = self.resources[job_id]['channel']
            status_command = "ps --pid {} | grep {}".format(self.resources[job_id]['job_id'],
                                                            self.resources[job_id]['cmd'].split()[0])
            retcode, stdout, stderr = channel.execute_wait(status_command)
            if retcode != 0 and self.resources[job_id]['status'].state == JobState.RUNNING:
                self.resources[job_id]['status'] = JobStatus(JobState.FAILED)

        return [self.resources[job_id]['status'] for job_id in job_ids]