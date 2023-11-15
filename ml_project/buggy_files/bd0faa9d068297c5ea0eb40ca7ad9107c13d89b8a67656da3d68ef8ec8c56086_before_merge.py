    def qualities_preferred(self):
        """Return preferred qualities."""
        return Quality.split_quality(self.quality)[1]