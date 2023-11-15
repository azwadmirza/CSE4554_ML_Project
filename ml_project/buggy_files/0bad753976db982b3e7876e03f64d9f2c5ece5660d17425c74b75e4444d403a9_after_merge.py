    def __getstate__(self):
        # pickling
        return (self._frames, com._pickle_array(self.items),
                com._pickle_array(self.major_axis),
                com._pickle_array(self.minor_axis),
                self.default_fill_value, self.default_kind)