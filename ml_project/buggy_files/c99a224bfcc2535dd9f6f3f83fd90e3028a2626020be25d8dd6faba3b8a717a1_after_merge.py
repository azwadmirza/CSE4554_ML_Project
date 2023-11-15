    def save_dataset(self, dataset, filename=None, fill_value=None, overlay=None, decorate=None, **kwargs):
        """Saves the *dataset* to a given *filename*.
        """
        fill_value = fill_value if fill_value is not None else self.fill_value
        img = get_enhanced_image(
            dataset.squeeze(), self.enhancer, fill_value, overlay=overlay, decorate=decorate)
        self.save_image(img, filename=filename, **kwargs)