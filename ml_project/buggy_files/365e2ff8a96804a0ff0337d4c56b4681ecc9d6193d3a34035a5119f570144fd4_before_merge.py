    def _list_partitions(self) -> List[str]:
        return [
            path
            for path in self._filesystem.find(self._path, **self._load_args)
            if path.endswith(self._filename_suffix)
        ]