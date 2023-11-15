    def memory_usage(self, deep=True) -> int:
        if self._use_arrow:
            return self.nbytes
        else:
            return pd.Series(self._ndarray).memory_usage(index=False, deep=deep)