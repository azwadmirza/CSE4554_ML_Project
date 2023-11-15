    def replace_job(self, job, newjob, recursive=True):
        """Replace given job with new job."""
        add_to_targetjobs = job in self.targetjobs

        depending = list(self.depending[job].items())
        if self.finished(job):
            self._finished.add(newjob)

        self.delete_job(job, recursive=recursive)

        if add_to_targetjobs:
            self.targetjobs.add(newjob)

        self.cache_job(newjob)

        self.update([newjob])

        logger.debug("Replace {} with dynamic branch {}".format(job, newjob))
        for job_, files in depending:
            # if not job_.dynamic_input:
            logger.debug("updating depending job {}".format(job_))
            self.dependencies[job_][newjob].update(files)
            self.depending[newjob][job_].update(files)