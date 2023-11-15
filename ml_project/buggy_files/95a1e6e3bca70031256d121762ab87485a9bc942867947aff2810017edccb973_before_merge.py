    def _sortJobsByResourceReq(self):
        job_types = list(self.jobQueueList.keys())
        # sorts from largest to smallest core usage
        # TODO: add a size() method to ResourceSummary and use it as the key. Ask me why.
        job_types.sort(key=lambda resourceRequirement: ResourceRequirement.cores)
        job_types.reverse()
        return job_types