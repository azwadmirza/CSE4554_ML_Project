    def __init__(self,
                 type,
                 callback,
                 strict=False,
                 pass_update_queue=False,
                 pass_job_queue=False):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue)
        self.type = type
        self.strict = strict