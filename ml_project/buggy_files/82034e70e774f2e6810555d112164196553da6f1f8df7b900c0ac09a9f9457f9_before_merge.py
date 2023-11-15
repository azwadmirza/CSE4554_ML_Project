    def to_timestamp(self, freq=None, how="start", copy=True):
        return self._default_to_pandas("to_timestamp", freq=freq, how=how, copy=copy)