    def watch(self):
        for new_schedulers in self._client.eternal_watch(SCHEDULER_PATH):
            self._cluster_info_ref.set_schedulers(new_schedulers)