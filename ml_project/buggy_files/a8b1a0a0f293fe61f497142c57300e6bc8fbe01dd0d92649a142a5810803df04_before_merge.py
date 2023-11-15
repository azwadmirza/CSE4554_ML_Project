    def __setitem__(self, key, value):
        if isinstance(key, basestring):
            self.coords[key] = value
        else:
            # xarray-style array indexing
            self.variable[key] = value