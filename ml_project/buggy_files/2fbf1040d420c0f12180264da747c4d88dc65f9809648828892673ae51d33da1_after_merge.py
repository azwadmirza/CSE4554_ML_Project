    def _vault_jobs_output_response(self, request, full_url, headers):
        vault_name = full_url.split("/")[-4]
        job_id = full_url.split("/")[-2]
        vault = self.backend.get_vault(vault_name)
        if vault.job_ready(job_id):
            output = vault.get_job_output(job_id)
            if isinstance(output, dict):
                headers['content-type'] = 'application/json'
                return 200, headers, json.dumps(output)
            else:
                headers['content-type'] = 'application/octet-stream'
                return 200, headers, output
        else:
            return 404, headers, "404 Not Found"