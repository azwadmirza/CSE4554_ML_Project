    def fetch_data(self, session_id, chunk_key, index_obj=None, compression_type=None):
        logger.debug('Sending data %s from %s', chunk_key, self.uid)
        if compression_type is None:
            compression_type = dataserializer.CompressType(options.worker.transfer_compression)
        if index_obj is None:
            if options.vineyard.socket:
                target_devs = [DataStorageDevice.VINEYARD, DataStorageDevice.DISK]  # pragma: no cover
            else:
                target_devs = [DataStorageDevice.SHARED_MEMORY, DataStorageDevice.DISK]
            ev = self._result_copy_ref.start_copy(session_id, chunk_key, target_devs)
            if ev:
                ev.wait(options.worker.prepare_data_timeout)

            reader = self.storage_client.create_reader(
                session_id, chunk_key, target_devs, packed=True,
                packed_compression=compression_type, _promise=False)

            with reader:
                pool = reader.get_io_pool()
                return pool.submit(reader.read).result()
        else:
            try:
                if options.vineyard.socket:
                    memory_device = DataStorageDevice.VINEYARD  # pragma: no cover
                else:
                    memory_device = DataStorageDevice.SHARED_MEMORY
                value = self.storage_client.get_object(
                    session_id, chunk_key, [memory_device], _promise=False)
            except IOError:
                reader = self.storage_client.create_reader(
                    session_id, chunk_key, [DataStorageDevice.DISK], packed=False, _promise=False)
                with reader:
                    pool = reader.get_io_pool()
                    value = dataserializer.deserialize(pool.submit(reader.read).result())

            try:
                sliced_value = value.iloc[tuple(index_obj)]
            except AttributeError:
                sliced_value = value[tuple(index_obj)]

            return self._serialize_pool.submit(
                dataserializer.dumps, sliced_value, compress=compression_type).result()