    def post_create(self):
        from ..graph import GraphActor
        from ..assigner import AssignerActor
        from ..chunkmeta import ChunkMetaActor
        from ..kvstore import KVStoreActor
        from ..resource import ResourceActor

        self.set_cluster_info_ref()
        self._assigner_ref = self.ctx.actor_ref(AssignerActor.default_name())
        self._chunk_meta_ref = self.ctx.actor_ref(ChunkMetaActor.default_name())
        self._graph_refs.append(self.get_actor_ref(GraphActor.gen_name(self._session_id, self._graph_ids[0])))
        self._resource_ref = self.get_actor_ref(ResourceActor.default_name())

        self._kv_store_ref = self.ctx.actor_ref(KVStoreActor.default_name())
        if not self.ctx.has_actor(self._kv_store_ref):
            self._kv_store_ref = None