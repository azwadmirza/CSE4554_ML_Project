    def fetch_data(self, session_id, tileable_key, index_obj=None, serial=True,
                   serial_type=None, compressions=None, pickle_protocol=None):
        session_uid = SessionActor.gen_uid(session_id)
        session_ref = self.get_actor_ref(session_uid)
        graph_ref = self.actor_client.actor_ref(
            session_ref.get_graph_ref_by_tileable_key(tileable_key))
        nsplits, chunk_keys, chunk_indexes = graph_ref.get_tileable_metas([tileable_key])[0]
        return self.fetch_chunks_data(session_id, chunk_indexes, chunk_keys, nsplits,
                                      index_obj=index_obj, serial=serial, serial_type=serial_type,
                                      compressions=compressions, pickle_protocol=pickle_protocol)