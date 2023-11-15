    def contains(self, pat, case=True, flags=0):
        result = str_contains(self.series, pat, case=case, flags=flags)
        return self._wrap_result(result)