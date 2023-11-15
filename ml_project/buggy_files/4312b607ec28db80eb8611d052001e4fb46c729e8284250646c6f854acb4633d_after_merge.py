    def finished(self, job, keep_metadata=True):
        if not keep_metadata:
            for f in job.expanded_output:
                self._delete_record(self._incomplete_path, f)
            return

        version = str(job.rule.version) if job.rule.version is not None else None
        code = self._code(job.rule)
        input = self._input(job)
        log = self._log(job)
        params = self._params(job)
        shellcmd = job.shellcmd
        conda_env = self._conda_env(job)
        fallback_time = time.time()
        for f in job.expanded_output:
            rec_path = self._record_path(self._incomplete_path, f)
            starttime = os.path.getmtime(rec_path) if os.path.exists(rec_path) else None
            # Sometimes finished is called twice, if so, lookup the previous starttime
            if not os.path.exists(rec_path):
                starttime = self._read_record(self._metadata_path, f).get(
                    "starttime", None
                )
            endtime = f.mtime.local_or_remote() if f.exists else fallback_time
            self._record(
                self._metadata_path,
                {
                    "version": version,
                    "code": code,
                    "rule": job.rule.name,
                    "input": input,
                    "log": log,
                    "params": params,
                    "shellcmd": shellcmd,
                    "incomplete": False,
                    "starttime": starttime,
                    "endtime": endtime,
                    "job_hash": hash(job),
                    "conda_env": conda_env,
                    "container_img_url": job.container_img_url,
                },
                f,
            )
            self._delete_record(self._incomplete_path, f)