    def cleanup(self, name, namespace, persistent):
        if namespace is None or name is None:
            raise ValueError("neither name nor namespace can be None")

        type = storage_basic_pb2.LMDB if persistent else storage_basic_pb2.IN_MEMORY

        storage_locator = storage_basic_pb2.StorageLocator(type=type, namespace=namespace, name=name)
        _table = _DTable(storage_locator=storage_locator)

        self.destroy_all(_table)

        LOGGER.debug("cleaned up: %s", _table)