    def __bool__(self):
        if self.original_string is None:
            return (self._components is not None and
                    (len(self._components) > 1 or bool(self._components[0])))
        return bool(self.original_string)