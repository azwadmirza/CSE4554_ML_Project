    def init(self, progress=False):
        """ Initialise the DAG. """
        for job in map(self.rule2job, self.targetrules):
            job = self.update([job], progress=progress)
            self.targetjobs.add(job)

        for file in self.targetfiles:
            job = self.update(self.file2jobs(file), file=file, progress=progress)
            self.targetjobs.add(job)

        self.cleanup()

        self.update_needrun()
        self.set_until_jobs()
        self.delete_omitfrom_jobs()
        self.update_jobids()

        self.check_directory_outputs()

        # check if remaining jobs are valid
        for i, job in enumerate(self.jobs):
            job.is_valid()