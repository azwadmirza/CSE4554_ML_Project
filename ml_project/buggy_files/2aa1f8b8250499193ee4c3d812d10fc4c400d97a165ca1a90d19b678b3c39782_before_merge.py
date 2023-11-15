    def _get_full_key(self, key: Union[str, Enum, int, None]) -> str:
        parent = self._get_parent()
        if parent is None:
            if self._metadata.key is None:
                return ""
            else:
                return str(self._metadata.key)
        else:
            return parent._get_full_key(self._metadata.key)