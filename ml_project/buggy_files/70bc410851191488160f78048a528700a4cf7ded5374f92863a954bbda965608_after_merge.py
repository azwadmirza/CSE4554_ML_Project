    def get_job_output(self, job_id):
        job = self.describe_job(job_id)
        jobj = job.to_dict()
        if jobj["Action"] == "InventoryRetrieval":
            archives = self.get_archive_list()
            return {
                "VaultARN": self.arn,
                "InventoryDate": jobj["CompletionDate"],
                "ArchiveList": archives
            }
        else:
            archive_body = self.get_archive_body(job.archive_id)
            return archive_body