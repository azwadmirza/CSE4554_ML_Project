    def apply_index(self, i):
        if self.weekday is None:
            return ((i.to_period('W') + self.n).to_timestamp() +
                    i.to_perioddelta('W'))
        else:
            return self._end_apply_index(i)