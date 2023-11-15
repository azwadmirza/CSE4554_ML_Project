    def status(self, job_ids):
        """Get the status of a list of jobs identified by their ids.
        Parameters
        ----------
        job_ids : list of str
            Identifiers for the jobs.
        Returns
        -------
        list of int
            The status codes of the requsted jobs.
        """
        statuses = []
        logger.info('List VMs in resource group')
        for job_id in job_ids:
            try:
                vm = self.compute_client.virtual_machines.get(
                    self.group_name, job_id, expand='instanceView')
                status = vm.instance_view.statuses[1].display_status
                statuses.append(JobStatus(translate_table.get(status, JobState.UNKNOWN)))
            # This only happens when it is in ProvisionState/Pending
            except IndexError:
                statuses.append(JobStatus(JobState.PENDING))
        return statuses