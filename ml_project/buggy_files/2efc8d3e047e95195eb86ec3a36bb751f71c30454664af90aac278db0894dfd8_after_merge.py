    def to_string_user(self):
        if self.is_local:
            return str(self.local_track_path.to_string_user())
        return str(self._raw)