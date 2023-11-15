    def _status(self):
        ''' Get the status of a list of jobs identified by the job identifiers
        returned from the submit request.

        Returns:
             - A list of JobStatus objects corresponding to each job_id in the job_ids list.

        Raises:
             - ExecutionProviderException or its subclasses

        '''

        cmd = "qstat"

        retcode, stdout, stderr = self.execute_wait(cmd)

        # Execute_wait failed. Do no update
        if retcode != 0:
            return

        jobs_missing = list(self.resources.keys())
        for line in stdout.split('\n'):
            parts = line.split()
            if parts and parts[0].lower().lower() != 'job-id' \
                    and not parts[0].startswith('----'):
                job_id = parts[0]
                status = translate_table.get(parts[4].lower(), JobState.UNKNOWN)
                if job_id in self.resources:
                    self.resources[job_id]['status'] = status
                    jobs_missing.remove(job_id)

        # Filling in missing blanks for jobs that might have gone missing
        # we might lose some information about why the jobs failed.
        for missing_job in jobs_missing:
            self.resources[missing_job]['status'] = JobStatus(JobState.COMPLETED)