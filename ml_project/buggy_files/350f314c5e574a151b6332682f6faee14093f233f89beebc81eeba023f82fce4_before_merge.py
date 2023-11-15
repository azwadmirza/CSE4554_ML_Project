    def fetch_chunk_data(self, session_id, chunk_key, index_obj=None):
        endpoints = self.chunk_meta_client.get_workers(session_id, chunk_key)
        if endpoints is None:
            raise KeyError(f'Chunk key {chunk_key} not exist in cluster')
        sender_ref = self.actor_client.actor_ref(ResultSenderActor.default_uid(),
                                                 address=random.choice(endpoints))
        return sender_ref.fetch_data(session_id, chunk_key, index_obj, _wait=False)