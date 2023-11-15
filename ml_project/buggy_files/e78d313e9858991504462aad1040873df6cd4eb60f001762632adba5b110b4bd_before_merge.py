    def to_string_user(self):
        if self.is_local:
            return str(self.track.to_string_hidden())
        return str(self._raw)