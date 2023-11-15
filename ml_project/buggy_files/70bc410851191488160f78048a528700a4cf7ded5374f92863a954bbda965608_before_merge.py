    def get_job_output(self, job_id):
        job = self.describe_job(job_id)
        archive_body = self.get_archive_body(job.archive_id)
        return archive_body