    def fetch_chunk_data(self, session_id, chunk_key, index_obj=None):
        endpoints = self.chunk_meta_client.get_workers(session_id, chunk_key)
        if endpoints is None:
            raise KeyError(f'Chunk key {chunk_key} not exist in cluster')

        source_endpoint = random.choice(endpoints)
        logger.debug('Fetching chunk %s from worker %s', chunk_key, source_endpoint)
        sender_ref = self.actor_client.actor_ref(ResultSenderActor.default_uid(),
                                                 address=source_endpoint)
        return sender_ref.fetch_data(session_id, chunk_key, index_obj, _wait=False)