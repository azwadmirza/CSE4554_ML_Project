    def create(self, session_id, chunk_key, size):
        from pyarrow.lib import PlasmaStoreFull
        obj_id = self._new_object_id(session_id, chunk_key)

        try:
            self._plasma_client.evict(size)
            buffer = self._plasma_client.create(obj_id, size)
            return buffer
        except PlasmaStoreFull:
            exc_type = PlasmaStoreFull
            self._mapper_ref.delete(session_id, chunk_key)
            logger.warning('Chunk %s(%d) failed to store to plasma due to StoreFullError',
                           chunk_key, size)
        except:  # noqa: E722  # pragma: no cover
            self._mapper_ref.delete(session_id, chunk_key)
            raise

        if exc_type is PlasmaStoreFull:
            raise StoreFull