    def pre_destroy(self):
        self._heartbeat_ref.destroy()
        self.unset_cluster_info_ref()
        super().pre_destroy()