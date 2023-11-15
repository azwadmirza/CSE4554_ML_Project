    def update_ready(self, jobs=None):
        """Update information whether a job is ready to execute.

        Given jobs must be needrun jobs!
        """

        if jobs is None:
            jobs = self.needrun_jobs

        potential_new_ready_jobs = False
        candidate_groups = set()
        for job in jobs:
            if job in self._ready_jobs or job in self._running:
                # job has been seen before or is running, no need to process again
                continue
            if not self.finished(job) and self._ready(job):
                potential_new_ready_jobs = True
                if job.group is None:
                    self._ready_jobs.add(job)
                else:
                    group = self._group[job]
                    group.finalize()
                    candidate_groups.add(group)

        self._ready_jobs.update(
            group
            for group in candidate_groups
            if all(self._ready(job) for job in group)
        )
        return potential_new_ready_jobs