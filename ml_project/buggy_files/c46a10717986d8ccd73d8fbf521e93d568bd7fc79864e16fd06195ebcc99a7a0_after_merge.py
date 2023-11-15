    def initiate_job(self, vault_name, job_type, tier, archive_id):
        vault = self.get_vault(vault_name)
        job_id = vault.initiate_job(job_type, tier, archive_id)
        return job_id