    def watch(self):
        for new_schedulers in self._client.eternal_watch(SCHEDULER_PATH):
            self._cluster_info_ref.set_schedulers([to_str(s) for s in new_schedulers])