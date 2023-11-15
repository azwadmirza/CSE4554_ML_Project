    def _list_partitions(self) -> List[str]:
        checkpoint = self._read_checkpoint()
        checkpoint_path = self._filesystem._strip_protocol(  # pylint: disable=protected-access
            self._checkpoint_config[self._filepath_arg]
        )

        def _is_valid_partition(partition) -> bool:
            if not partition.endswith(self._filename_suffix):
                return False
            if partition == checkpoint_path:
                return False
            if checkpoint is None:
                # nothing was processed yet
                return True
            partition_id = self._path_to_partition(partition)
            return self._comparison_func(partition_id, checkpoint)

        return [
            part
            for part in sorted(self._filesystem.find(self._path, **self._load_args))
            if _is_valid_partition(part)
        ]