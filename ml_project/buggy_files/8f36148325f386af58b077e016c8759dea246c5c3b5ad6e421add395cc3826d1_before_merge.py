    def update(self, other):
        return self._default_to_pandas(pandas.Series.update, other)