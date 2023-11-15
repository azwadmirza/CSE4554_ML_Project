    def pre_destroy(self):
        super().pre_destroy()
        self._manager_ref.delete_session(self._session_id, _tell=True)
        self.ctx.destroy_actor(self._assigner_ref)
        for graph_ref in self._graph_refs.values():
            self.ctx.destroy_actor(graph_ref)
        for mut_tensor_ref in self._mut_tensor_refs.values():
            self.ctx.destroy_actor(mut_tensor_ref)