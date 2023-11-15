    def qualities_allowed(self):
        """Return allowed qualities."""
        return Quality.split_quality(self.quality)[0]