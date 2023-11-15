    def create_reader(self, session_id, data_key, source_devices, packed=False,
                      packed_compression=None, _promise=True):
        """
        Create a data reader from existing data and return in a Promise.
        If no readers can be created, will try copying the data into a
        readable storage.

        :param session_id: session id
        :param data_key: data key
        :param source_devices: devices to read from
        :param packed: create a reader to read packed data format
        :param packed_compression: compression format to use when reading as packed
        :param _promise: return a promise
        """
        source_devices = self._normalize_devices(source_devices)
        stored_devs = set(self._manager_ref.get_data_locations(session_id, [data_key])[0])
        for src_dev in source_devices:
            if src_dev not in stored_devs:
                continue
            handler = self.get_storage_handler(src_dev)
            try:
                logger.debug('Creating %s reader for (%s, %s) on %s', 'packed' if packed else 'bytes',
                             session_id, data_key, handler.storage_type)
                return handler.create_bytes_reader(
                    session_id, data_key, packed=packed, packed_compression=packed_compression,
                    _promise=_promise)
            except AttributeError:  # pragma: no cover
                raise IOError(f'Device {src_dev} does not support direct reading.')

        if _promise:
            return self.copy_to(session_id, [data_key], source_devices) \
                .then(lambda *_: self.create_reader(session_id, data_key, source_devices, packed=packed))
        else:
            raise IOError('Cannot return a non-promise result')