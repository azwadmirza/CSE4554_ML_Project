    def __setstate__(self, state):
        self.__dict__.update({k: v for k, v in six.iteritems(state) if k != "value"})

        self._value_buffer = tempfile.SpooledTemporaryFile(
            max_size=self._max_buffer_size
        )
        self.value = state["value"]