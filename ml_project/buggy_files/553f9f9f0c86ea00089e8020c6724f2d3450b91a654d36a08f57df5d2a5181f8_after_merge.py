    def create(self, session_id, data_key, size):
        obj_id = self._new_object_id(session_id, data_key)
        try:
            self._plasma_client.evict(size)
            buffer = self._plasma_client.create(obj_id, size)
            return buffer
        except plasma_errors.PlasmaStoreFull:
            exc_type = plasma_errors.PlasmaStoreFull
            self._mapper_ref.delete(session_id, data_key)
            logger.warning('Data %s(%d) failed to store to plasma due to StorageFull',
                           data_key, size)
        except:  # noqa: E722
            self._mapper_ref.delete(session_id, data_key)
            raise

        if exc_type is plasma_errors.PlasmaStoreFull:
            raise StorageFull(request_size=size, capacity=self._size_limit, affected_keys=[data_key])