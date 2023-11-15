    def get(self, session_id, chunk_key):
        """
        Get deserialized Mars object from plasma store
        """
        from pyarrow.plasma import ObjectNotAvailable

        obj_id = self._get_object_id(session_id, chunk_key)
        obj = self._plasma_client.get(obj_id, serialization_context=self._serialize_context, timeout_ms=10)
        if obj is ObjectNotAvailable:
            raise KeyError('(%r, %r)' % (session_id, chunk_key))
        return obj