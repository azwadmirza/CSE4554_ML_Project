    def _load(self) -> Dict[str, Callable[[], Any]]:
        partitions = {}

        for partition in self._list_partitions():
            partition_id = self._path_to_partition(partition)
            kwargs = deepcopy(self._dataset_config)
            # join the protocol back since PySpark may rely on it
            kwargs[self._filepath_arg] = self._join_protocol(partition)
            partitions[partition_id] = self._dataset_type(  # type: ignore
                **kwargs
            ).load()

        return partitions