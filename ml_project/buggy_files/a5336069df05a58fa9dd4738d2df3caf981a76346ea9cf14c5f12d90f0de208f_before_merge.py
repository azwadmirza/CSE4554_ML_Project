    def __getitem__(self, key):
        if isinstance(key, tuple):
            try:
                return self.obj.get_value(*key)
            except Exception:
                pass

            return self._getitem_tuple(key)
        else:
            return self._getitem_axis(key, axis=0)