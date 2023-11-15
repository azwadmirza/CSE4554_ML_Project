    def get_actual_size(self, session_id, chunk_key):
        """
        Get actual size of Mars object from plasma store
        """
        buf = None
        try:
            obj_id = self._get_object_id(session_id, chunk_key)
            [buf] = self._plasma_client.get_buffers([obj_id], timeout_ms=10)
            if buf is None:
                raise KeyError((session_id, chunk_key))
            size = buf.size
        finally:
            del buf
        return size