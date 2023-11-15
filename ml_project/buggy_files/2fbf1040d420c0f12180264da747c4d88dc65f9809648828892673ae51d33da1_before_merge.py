    def _vault_jobs_output_response(self, request, full_url, headers):
        vault_name = full_url.split("/")[-4]
        job_id = full_url.split("/")[-2]

        vault = self.backend.get_vault(vault_name)
        output = vault.get_job_output(job_id)
        headers['content-type'] = 'application/octet-stream'
        return 200, headers, output