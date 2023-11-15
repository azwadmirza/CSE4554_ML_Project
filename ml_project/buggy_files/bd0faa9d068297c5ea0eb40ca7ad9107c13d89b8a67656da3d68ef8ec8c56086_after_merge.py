    def qualities_preferred(self, qualities_preferred):
        """Configure qualities (combined) by adding the preferred qualities to it."""
        self.quality = Quality.combine_qualities(self.qualities_allowed, qualities_preferred)