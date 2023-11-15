    def shape(self):
        if self._use_arrow:
            return (self._arrow_array.length(), )
        else:
            return self._ndarray.shape