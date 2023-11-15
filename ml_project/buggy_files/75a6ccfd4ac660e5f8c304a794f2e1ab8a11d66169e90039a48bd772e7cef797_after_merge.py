    def __getitem__(self, item):
        """
        Retrieve column or slice from DataFrame
        """
        try:
            # unsure about how kludgy this is
            s = self._series[item]
            s.name = item
            return s
        except (TypeError, KeyError):
            if isinstance(item, slice):
                date_rng = self.index[item]
                return self.reindex(date_rng)

            elif isinstance(item, np.ndarray):
                if len(item) != len(self.index):
                    raise Exception('Item wrong length %d instead of %d!' %
                                    (len(item), len(self.index)))
                newIndex = self.index[item]
                return self.reindex(newIndex)
            else: # pragma: no cover
                raise