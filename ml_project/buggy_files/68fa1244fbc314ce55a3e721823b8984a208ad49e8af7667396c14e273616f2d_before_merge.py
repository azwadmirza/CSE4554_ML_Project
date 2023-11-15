    def shape(self):
        """Return shape of first image in subject.

        Consistency of shapes across images in the subject is checked first.
        """
        self.check_consistent_shape()
        image = self.get_images(intensity_only=False)[0]
        return image.shape