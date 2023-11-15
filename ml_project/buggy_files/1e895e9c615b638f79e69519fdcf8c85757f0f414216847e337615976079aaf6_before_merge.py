    def put(self, session_id, chunk_key, value):
        """
        Put a Mars object into plasma store
        :param session_id: session id
        :param chunk_key: chunk key
        :param value: Mars object to be put
        """
        import pyarrow
        from pyarrow.lib import PlasmaStoreFull
        from ..serialize.dataserializer import DataTuple

        data_size = calc_data_size(value)
        if isinstance(value, tuple):
            value = DataTuple(*value)

        try:
            obj_id = self._new_object_id(session_id, chunk_key)
        except StoreKeyExists:
            obj_id = self._get_object_id(session_id, chunk_key)
            if self._plasma_client.contains(obj_id):
                logger.debug('Chunk %s already exists, returning existing', chunk_key)
                [buffer] = self._plasma_client.get_buffers([obj_id], timeout_ms=10)
                return buffer
            else:
                logger.warning('Chunk %s registered but no data found, reconstructed', chunk_key)
                self.delete(session_id, chunk_key)
                obj_id = self._new_object_id(session_id, chunk_key)

        try:
            serialized = pyarrow.serialize(value, self._serialize_context)
            try:
                buffer = self._plasma_client.create(obj_id, serialized.total_bytes)
                stream = pyarrow.FixedSizeBufferWriter(buffer)
                stream.set_memcopy_threads(6)
                serialized.write_to(stream)
                self._plasma_client.seal(obj_id)
            finally:
                del serialized
            return buffer
        except PlasmaStoreFull:
            self._mapper_ref.delete(session_id, chunk_key)
            logger.warning('Chunk %s(%d) failed to store to plasma due to StoreFullError',
                           chunk_key, data_size)
            exc = PlasmaStoreFull

        if exc is PlasmaStoreFull:
            raise StoreFull