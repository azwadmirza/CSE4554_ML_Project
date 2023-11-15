    def _vault_jobs_response(self, request, full_url, headers):
        method = request.method
        if hasattr(request, 'body'):
            body = request.body
        else:
            body = request.data
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
            job_type = json_body['Type']
            archive_id = None
            if 'ArchiveId' in json_body:
                archive_id = json_body['ArchiveId']
            if 'Tier' in json_body:
                tier = json_body["Tier"]
            else:
                tier = "Standard"
            job_id = self.backend.initiate_job(vault_name, job_type, tier, archive_id)
            headers['x-amz-job-id'] = job_id
            headers['Location'] = "/{0}/vaults/{1}/jobs/{2}".format(account_id, vault_name, job_id)
            return 202, headers, ""