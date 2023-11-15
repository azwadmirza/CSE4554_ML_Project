    def isna(self):
        if not self._force_use_pandas and self._use_arrow and \
                hasattr(self._arrow_array, 'is_null'):
            return self._arrow_array.is_null().to_pandas().to_numpy()
        elif self._use_arrow:
            return pd.isna(self._arrow_array.to_pandas()).to_numpy()
        else:
            return pd.isna(self._ndarray)