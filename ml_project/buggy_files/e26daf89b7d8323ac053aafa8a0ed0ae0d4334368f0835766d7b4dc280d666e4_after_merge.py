    def show(self, dataset_id, overlay=None):
        """Show the *dataset* on screen as an image."""
        from satpy.writers import get_enhanced_image
        img = get_enhanced_image(self[dataset_id].squeeze(), overlay=overlay)
        img.show()
        return img