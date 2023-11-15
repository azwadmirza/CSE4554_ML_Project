    def __getstate__(self):
        # pickling
        return (self._frames, _pickle_array(self.items),
                _pickle_array(self.major_axis), _pickle_array(self.minor_axis),
                self.default_fill_value, self.default_kind)