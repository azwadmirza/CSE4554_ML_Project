    def suffix(self):
        if self.is_local:
            return self.track.suffix
        return None