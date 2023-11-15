    def qualities_allowed(self, qualities_allowed):
        """Configure qualities (combined) by adding the allowed qualities to it."""
        self.quality = Quality.combine_qualities(qualities_allowed, self.qualities_preferred)