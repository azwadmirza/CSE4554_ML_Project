    def _parse_path(
            self,
            path: Union[TypePath, Sequence[TypePath]]
            ) -> Optional[Union[Path, List[Path]]]:
        if path is None:
            return None
        if isinstance(path, (str, Path)):
            return self._parse_single_path(path)
        else:
            return [self._parse_single_path(p) for p in path]