    def scale_in(self, n, force=True, max_idletime=None):
        if force and not max_idletime:
            ids = self._executor.scale_in(n)
        else:
            ids = self._executor.scale_in(n, force=force, max_idletime=max_idletime)
        if ids is not None:
            new_status = {}
            for id in ids:
                new_status[id] = JobStatus(JobState.CANCELLED)
                del self._status[id]
            self.send_monitoring_info(new_status, block_id_type='internal')
        return ids