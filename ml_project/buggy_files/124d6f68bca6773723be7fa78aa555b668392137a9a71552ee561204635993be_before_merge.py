    def put(self, session_id, data_key, value):
        """
        Put a Mars object into plasma store
        :param session_id: session id
        :param data_key: chunk key
        :param value: Mars object to be put
        """
        data_size = None

        try:
            obj_id = self._new_object_id(session_id, data_key)
        except StorageDataExists:
            obj_id = self._get_object_id(session_id, data_key)
            if self._plasma_client.contains(obj_id):
                logger.debug('Data %s already exists, returning existing', data_key)
                [buffer] = self._plasma_client.get_buffers([obj_id], timeout_ms=10)
                del value
                return buffer
            else:
                logger.warning('Data %s registered but no data found, reconstructed', data_key)
                self._mapper_ref.delete(session_id, data_key)
                obj_id = self._new_object_id(session_id, data_key)

        try:
            try:
                serialized = dataserializer.serialize(value)
            except SerializationCallbackError:
                self._mapper_ref.delete(session_id, data_key)
                raise SerializationFailed(obj=value) from None

            del value
            data_size = serialized.total_bytes
            try:
                buffer = self._plasma_client.create(obj_id, serialized.total_bytes)
                stream = pyarrow.FixedSizeBufferWriter(buffer)
                stream.set_memcopy_threads(6)
                self._pool.submit(serialized.write_to, stream).result()
                self._plasma_client.seal(obj_id)
            finally:
                del serialized
            return buffer
        except PlasmaStoreFull:
            self._mapper_ref.delete(session_id, data_key)
            logger.warning('Data %s(%d) failed to store to plasma due to StorageFull',
                           data_key, data_size)
            exc = PlasmaStoreFull
        except:  # noqa: E722
            self._mapper_ref.delete(session_id, data_key)
            raise

        if exc is PlasmaStoreFull:
            raise StorageFull(request_size=data_size, capacity=self._size_limit,
                              affected_keys=[data_key])