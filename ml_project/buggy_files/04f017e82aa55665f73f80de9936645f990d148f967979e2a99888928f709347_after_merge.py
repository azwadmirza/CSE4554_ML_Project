    def __getitem__(self, key):
        try:
            return self.index.get_value(self, key)

        except InvalidIndexError:
            pass
        except KeyError:
            if isinstance(key, (int, np.integer)):
                return self._get_val_at(key)
            elif key is Ellipsis:
                return self
            raise Exception('Requested index not in this series!')

        except TypeError:
            # Could not hash item, must be array-like?
            pass

        key = _values_from_object(key)
        if self.index.nlevels > 1 and isinstance(key, tuple):
            # to handle MultiIndex labels
            key = self.index.get_loc(key)
        return self._constructor(self.values[key],
                                 index=self.index[key]).__finalize__(self)