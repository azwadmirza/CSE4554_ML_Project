    def _values_(self):
        return [getattr(self, k, None) for k in self.__slots__
                if k not in self._no_copy_attrs_]