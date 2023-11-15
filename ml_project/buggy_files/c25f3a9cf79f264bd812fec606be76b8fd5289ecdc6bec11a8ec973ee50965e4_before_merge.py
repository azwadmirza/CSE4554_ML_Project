    def pre_destroy(self):
        super().pre_destroy()
        self._graph_meta_ref.destroy()