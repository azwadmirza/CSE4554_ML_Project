    def initiate_job(self, archive_id):
        job_id = get_job_id()
        job = ArchiveJob(job_id, archive_id)
        self.jobs[job_id] = job
        return job_id