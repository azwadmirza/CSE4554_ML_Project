    def __call__(self, data):
        """
        Raises:
            KeyError: When a key in ``self.names`` already exists in ``data``.

        """
        d = dict(data)
        for key, new_key in zip(self.keys * self.times, self.names):
            if new_key in d:
                raise KeyError(f"Key {new_key} already exists in data.")
            d[new_key] = copy.deepcopy(d[key])
        return d