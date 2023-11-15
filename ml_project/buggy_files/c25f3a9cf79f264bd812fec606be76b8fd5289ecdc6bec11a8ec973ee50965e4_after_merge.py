    def pre_destroy(self):
        super().pre_destroy()
        self.unset_cluster_info_ref()
        self._graph_meta_ref.destroy()