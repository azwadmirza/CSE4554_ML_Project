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

        all_states = []

        status = self.client.describe_instances(InstanceIds=list(job_ids))
        for r in status['Reservations']:
            for i in r['Instances']:
                instance_id = i['InstanceId']
                instance_state = translate_table.get(i['State']['Name'], JobState.UNKNOWN)
                self.resources[instance_id]['status'] = JobStatus(instance_state)
                all_states.extend([instance_state])

        return all_states