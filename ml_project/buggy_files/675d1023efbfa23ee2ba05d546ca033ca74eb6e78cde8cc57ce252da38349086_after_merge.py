    def split(self, pat=None, n=0):
        result = str_split(self.series, pat, n=n)
        return self._wrap_result(result)