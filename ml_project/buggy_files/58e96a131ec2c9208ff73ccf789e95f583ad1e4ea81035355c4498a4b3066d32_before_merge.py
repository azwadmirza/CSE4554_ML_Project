    def __getitem__(self, indx):
        """
        Get the index.

        """
        m = self._mask
        if m is not nomask and m[indx]:
            return masked
        return self._data[indx]