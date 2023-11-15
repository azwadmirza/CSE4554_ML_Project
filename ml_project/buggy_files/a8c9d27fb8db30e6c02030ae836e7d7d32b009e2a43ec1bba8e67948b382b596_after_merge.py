    def _add_dependencies(self, key: Key, value: Key = None) -> None:
        if value is None:
            value = key
        else:
            self.dependencies.setdefault(key, set()).add(value)
        for elt in key:
            if isinstance(elt, Key):
                self._add_dependencies(elt, value)