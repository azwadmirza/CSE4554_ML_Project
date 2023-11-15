    def initiate_job(self, vault_name, archive_id):
        vault = self.get_vault(vault_name)
        job_id = vault.initiate_job(archive_id)
        return job_id