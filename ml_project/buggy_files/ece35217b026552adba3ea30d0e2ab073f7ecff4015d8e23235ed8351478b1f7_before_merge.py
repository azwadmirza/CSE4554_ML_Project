    def _vault_jobs_response(self, request, full_url, headers):
        method = request.method
        body = request.body
        account_id = full_url.split("/")[1]
        vault_name = full_url.split("/")[-2]

        if method == 'GET':
            jobs = self.backend.list_jobs(vault_name)
            headers['content-type'] = 'application/json'
            return 200, headers, json.dumps({
                "JobList": [
                    job.to_dict() for job in jobs
                ],
                "Marker": None,
            })
        elif method == 'POST':
            json_body = json.loads(body.decode("utf-8"))
            archive_id = json_body['ArchiveId']
            job_id = self.backend.initiate_job(vault_name, archive_id)
            headers['x-amz-job-id'] = job_id
            headers[
                'Location'] = "/{0}/vaults/{1}/jobs/{2}".format(account_id, vault_name, job_id)
            return 202, headers, ""