    def size(self):
        return pandas.Series({k: len(v) for k, v in self._index_grouped.items()})