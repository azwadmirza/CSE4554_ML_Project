    def __init__(self, storage_locator, partitions=1):
        self.__client = _EggRoll.get_instance()
        self._namespace = storage_locator.namespace
        self._name = storage_locator.name
        self._type = storage_basic_pb2.StorageType.Name(storage_locator.type)
        self._partitions = partitions
        self.schema = {}