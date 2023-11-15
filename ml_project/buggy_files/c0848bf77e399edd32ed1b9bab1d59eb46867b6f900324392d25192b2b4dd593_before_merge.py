    def get_rectangle_cropping(self, workspace, orig_image):
        """Crop into a rectangle using user-specified coordinates"""
        cropping = np.ones(orig_image.pixel_data.shape[:2], bool)
        if not self.horizontal_limits.unbounded_min:
            cropping[:, :self.horizontal_limits.min] = False
        if not self.horizontal_limits.unbounded_max:
            cropping[:, self.horizontal_limits.max:] = False
        if not self.vertical_limits.unbounded_min:
            cropping[:self.vertical_limits.min, :] = False
        if not self.vertical_limits.unbounded_max:
            cropping[self.vertical_limits.max:, :] = False
        return cropping