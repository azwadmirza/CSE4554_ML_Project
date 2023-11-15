    def scale_in(self, n):
        ids = self._executor.scale_in(n)
        if ids is not None:
            new_status = {}
            for id in ids:
                new_status[id] = JobStatus(JobState.CANCELLED)
                del self._status[id]
            self.send_monitoring_info(new_status, block_id_type='internal')
        return ids