    def get_buffer(self, session_id, chunk_key):
        """
        Get raw buffer from plasma store
        """
        obj_id = self._get_object_id(session_id, chunk_key)
        [buf] = self._plasma_client.get_buffers([obj_id], timeout_ms=10)
        if buf is None:
            raise KeyError((session_id, chunk_key))
        return buf