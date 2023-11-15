    def __getitem__(self, key):
        try:
            return self.index.get_value(self, key)
        except InvalidIndexError:
            pass
        except KeyError:
            if isinstance(key, tuple) and isinstance(self.index, MultiIndex):
                # kludge
                pass
            else:
                raise
        except Exception:
            raise

        if com.is_iterator(key):
            key = list(key)

        # boolean
        # special handling of boolean data with NAs stored in object
        # arrays. Since we can't represent NA with dtype=bool
        if _is_bool_indexer(key):
            key = self._check_bool_indexer(key)
            key = np.asarray(key, dtype=bool)

        return self._get_with(key)