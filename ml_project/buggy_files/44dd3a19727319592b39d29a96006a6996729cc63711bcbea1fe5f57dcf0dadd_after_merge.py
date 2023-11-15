    def __getitem__(self, key):
        """
        Retrieve column or slice from DataFrame
        """
        try:
            # unsure about how kludgy this is
            s = self._series[key]
            s.name = key
            return s
        except (TypeError, KeyError):
            if isinstance(key, slice):
                date_rng = self.index[key]
                return self.reindex(date_rng)

            elif isinstance(key, (np.ndarray, list)):
                if isinstance(key, list):
                    key = lib.list_to_object_array(key)

                # also raises Exception if object array with NA values
                if com._is_bool_indexer(key):
                    key = np.asarray(key, dtype=bool)
                return self._getitem_array(key)
            else: # pragma: no cover
                raise