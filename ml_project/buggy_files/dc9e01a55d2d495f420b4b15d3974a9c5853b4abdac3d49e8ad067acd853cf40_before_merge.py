    def update_checkpoint_dependencies(self, jobs=None):
        """Update dependencies of checkpoints."""
        updated = False
        self.update_checkpoint_outputs()
        if jobs is None:
            jobs = [job for job in self.jobs if not self.needrun(job)]
        for job in jobs:
            if job.is_checkpoint:
                depending = list(self.depending[job])
                # re-evaluate depending jobs, replace and update DAG
                for j in depending:
                    logger.info("Updating job {} ({}).".format(self.jobid(j), j))
                    newjob = j.updated()
                    self.replace_job(j, newjob, recursive=False)
                    updated = True
        if updated:
            self.postprocess()
        return updated