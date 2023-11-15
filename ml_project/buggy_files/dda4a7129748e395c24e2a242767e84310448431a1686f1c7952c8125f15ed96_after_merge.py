    def __init__(self, job_id, tier, arn, archive_id):
        self.job_id = job_id
        self.tier = tier
        self.arn = arn
        self.archive_id = archive_id
        Job.__init__(self, tier)