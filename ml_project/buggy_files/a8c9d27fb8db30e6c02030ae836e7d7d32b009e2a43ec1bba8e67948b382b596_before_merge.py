    def _add_dependencies(self, key: Key, value: Key = None) -> None:
        if value is None:
            value = key
        else:
            self.dependencies.setdefault(key, set()).add(value)
        if isinstance(key, tuple):
            for elt in key:
                self._add_dependencies(elt, value)