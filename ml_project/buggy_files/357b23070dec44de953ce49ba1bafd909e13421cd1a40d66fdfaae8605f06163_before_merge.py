    def banner(self):
        """Return banner path."""
        img_type = image_cache.POSTER
        return image_cache.get_artwork(img_type, self.series_id)