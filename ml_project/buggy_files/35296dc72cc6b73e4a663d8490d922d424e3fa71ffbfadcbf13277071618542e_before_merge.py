    def register_running(self, jobs):
        self._ready_jobs -= jobs
        for job in jobs:
            try:
                del self._n_until_ready[job]
            except KeyError:
                # already gone
                pass