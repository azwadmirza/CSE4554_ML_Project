    def __setitem__(self, key, value):
        if not isinstance(key, str):
            return self._default_to_pandas(pandas.DataFrame.__setitem__, key, value)
        if key not in self.columns:
            self.insert(loc=len(self.columns), column=key, value=value)
        else:
            loc = self.columns.get_loc(key)
            self.__delitem__(key)
            self.insert(loc=loc, column=key, value=value)