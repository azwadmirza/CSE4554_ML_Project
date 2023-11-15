    def pre_destroy(self):
        self._actual_ref.destroy()
        self.unset_cluster_info_ref()