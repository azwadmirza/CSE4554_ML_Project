    def create(self, session_id, chunk_key, size):
        from pyarrow.lib import PlasmaStoreFull
        obj_id = self._new_object_id(session_id, chunk_key)

        try:
            buffer = self._plasma_client.create(obj_id, size)
            return buffer
        except PlasmaStoreFull:
            exc_type = PlasmaStoreFull
            logger.warning('Chunk %s(%d) failed to store to plasma due to StoreFullError',
                           chunk_key, size)

        if exc_type is PlasmaStoreFull:
            raise StoreFull