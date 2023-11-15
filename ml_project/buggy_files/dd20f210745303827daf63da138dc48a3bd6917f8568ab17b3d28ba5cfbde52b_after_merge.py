    def seal(self, session_id, chunk_key):
        from pyarrow.lib import PlasmaObjectNonexistent
        obj_id = self._get_object_id(session_id, chunk_key)
        try:
            self._plasma_client.seal(obj_id)
        except PlasmaObjectNonexistent:
            raise KeyError((session_id, chunk_key))