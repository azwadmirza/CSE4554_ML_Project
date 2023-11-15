    def spatial_shape(self):
        """Return spatial shape of first image in subject.

        Consistency of spatial shapes across images in the subject is checked
        first.
        """
        self.check_consistent_spatial_shape()
        return self.get_first_image().spatial_shape