    def status(self, job_ids):
        """Get the status of a list of jobs identified by their ids.

        Parameters
        ----------
        job_ids : list of int
            Identifiers of jobs for which the status will be returned.

        Returns
        -------
        List of int
            Status codes for the requested jobs.

        """
        self._status()
        return [self.resources[jid]['status'] for jid in job_ids]