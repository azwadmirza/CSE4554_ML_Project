    def __getitem__(self, item):
        if isinstance(item, int):
            item = slice(item, item + 1)
        ret = type(self)(self.table[item])
        ret.query_args = self.query_args
        ret.requests = self.requests
        ret.client = self._client

        warnings.warn("Downloading of sliced JSOC results is not supported. "
                      "All the files present in the original response will be downloaded.",
                      SunpyUserWarning)
        return ret