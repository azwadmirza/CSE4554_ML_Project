    def __init__(self,
                 type,
                 callback,
                 strict=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 run_async=False):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            run_async=run_async)
        self.type = type
        self.strict = strict