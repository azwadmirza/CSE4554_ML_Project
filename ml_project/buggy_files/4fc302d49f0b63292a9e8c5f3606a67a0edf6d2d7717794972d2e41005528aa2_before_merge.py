    def poster(self):
        """Return poster path."""
        img_type = image_cache.POSTER
        return image_cache.get_artwork(img_type, self.series_id)