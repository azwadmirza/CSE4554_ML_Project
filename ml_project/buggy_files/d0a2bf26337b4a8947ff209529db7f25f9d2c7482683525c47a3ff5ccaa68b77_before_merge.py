    def __getitem__(self, key):
        if self.ndim != 1 or not is_scalar(key):
            # FIXME: is_scalar check is a kludge
            return super().__getitem__(key)

        # Like Index.get_value, but we do not allow positional fallback
        obj = self.obj
        loc = obj.index.get_loc(key)
        return obj.index._get_values_for_loc(obj, loc, key)