    def initiate_job(self, job_type, tier, archive_id):
        job_id = get_job_id()

        if job_type == "inventory-retrieval":
            job = InventoryJob(job_id, tier, self.arn)
        elif job_type == "archive-retrieval":
            job = ArchiveJob(job_id, tier, self.arn, archive_id)

        self.jobs[job_id] = job
        return job_id