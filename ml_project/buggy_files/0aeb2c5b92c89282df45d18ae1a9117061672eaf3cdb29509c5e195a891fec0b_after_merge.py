    def seal(self, session_id, data_key):
        obj_id = self._get_object_id(session_id, data_key)
        try:
            self._plasma_client.seal(obj_id)
        except plasma_errors.PlasmaObjectNotFound:
            self._mapper_ref.delete(session_id, data_key)
            raise KeyError((session_id, data_key))