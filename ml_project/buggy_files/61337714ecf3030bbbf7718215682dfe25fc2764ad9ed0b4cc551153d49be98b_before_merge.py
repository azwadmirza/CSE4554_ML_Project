    def launch(self, job_overrides):
        import submitit

        num_jobs = len(job_overrides)
        assert num_jobs > 0
        self.config.hydra.job.num_jobs = num_jobs
        if self.queue == "auto":
            executor = submitit.AutoExecutor(
                folder=self.folder, conda_file=self.conda_file
            )
        elif self.queue == "slurm":
            executor = submitit.SlurmExecutor(folder=self.folder)
        elif self.queue == "chronos":
            executor = submitit.ChronosExecutor(
                folder=self.folder, conda_file=self.conda_file
            )
        elif self.queue == "local":
            executor = submitit.LocalExecutor(folder=self.folder)
        else:
            raise RuntimeError("Unsupported queue type {}".format(self.queue))

        executor.update_parameters(**self.queue_parameters[self.queue])

        log.info("Sweep output dir : {}".format(self.config.hydra.sweep.dir))
        path_str = str(self.config.hydra.sweep.dir)
        os.makedirs(path_str, exist_ok=True)
        if self.config.hydra.sweep.mode is not None:
            mode = int(str(self.config.hydra.sweep.mode), 8)
            os.chmod(path_str, mode=mode)

        jobs = []
        for job_num in range(num_jobs):
            sweep_override = list(job_overrides[job_num])
            log.info(
                "\t#{} : {}".format(
                    job_num,
                    " ".join(
                        hydra.plugins.common.utils.filter_overrides(sweep_override)
                    ),
                )
            )
            job = executor.submit(
                self.launch_job, sweep_override, "hydra.sweep.dir", job_num
            )
            jobs.append(job)

        return [j.results() for j in jobs]