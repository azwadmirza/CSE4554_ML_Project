    def finish(self, job, update_dynamic=True):
        """Finish a given job (e.g. remove from ready jobs, mark depending jobs
        as ready)."""

        self._running.remove(job)

        # turn off this job's Reason
        self.reason(job).mark_finished()

        try:
            self._ready_jobs.remove(job)
        except KeyError:
            pass

        if job.is_group():
            jobs = job
        else:
            jobs = [job]

        self._finished.update(jobs)

        updated_dag = False
        if update_dynamic:
            updated_dag = self.update_checkpoint_dependencies(jobs)

        depending = [
            j
            for job in jobs
            for j in self.depending[job]
            if not self.in_until(job) and self.needrun(j)
        ]

        if not updated_dag:
            # Mark depending jobs as ready.
            # Skip jobs that are marked as until jobs.
            # This is not necessary if the DAG has been fully updated above.
            for job in depending:
                self._n_until_ready[job] -= 1

        potential_new_ready_jobs = self.update_ready(depending)

        for job in jobs:
            if update_dynamic and job.dynamic_output:
                logger.info("Dynamically updating jobs")
                newjob = self.update_dynamic(job)
                if newjob:
                    # simulate that this job ran and was finished before
                    self.omitforce.add(newjob)
                    self._needrun.add(newjob)
                    self._finished.add(newjob)
                    updated_dag = True

                    self.postprocess()
                    self.handle_protected(newjob)
                    self.handle_touch(newjob)

        if updated_dag:
            # We might have new jobs, so we need to ensure that all conda envs
            # and singularity images are set up.
            if self.workflow.use_singularity:
                self.pull_container_imgs()
            if self.workflow.use_conda:
                self.create_conda_envs()
            potential_new_ready_jobs = True

        return potential_new_ready_jobs