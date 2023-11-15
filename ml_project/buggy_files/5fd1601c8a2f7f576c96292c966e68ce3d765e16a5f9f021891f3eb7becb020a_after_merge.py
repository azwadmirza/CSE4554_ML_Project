    def status(self, job_ids: List[Any]) -> List[JobStatus]:
        '''  Get the status of a list of jobs identified by their ids.

        Args:
            - job_ids (List of ids) : List of identifiers for the jobs

        Returns:
            - List of status codes.

        '''

        logger.debug("Checking status of: {0}".format(job_ids))
        for job_id in self.resources:

            retcode, stdout, stderr = self.channel.execute_wait('ps -p {} > /dev/null 2> /dev/null; echo "STATUS:$?" '.format(
                self.resources[job_id]['remote_pid']), self.cmd_timeout)
            if stdout:  # (is not None)
                for line in stdout.split('\n'):
                    if line.startswith("STATUS:"):
                        status = line.split("STATUS:")[1].strip()
                        if status == "0":
                            self.resources[job_id]['status'] = JobStatus(JobState.RUNNING)
                        else:
                            self.resources[job_id]['status'] = JobStatus(JobState.FAILED)

        return [self.resources[jid]['status'] for jid in job_ids]