    def suffix(self):
        if self.is_local:
            return self.local_track_path.suffix
        return None