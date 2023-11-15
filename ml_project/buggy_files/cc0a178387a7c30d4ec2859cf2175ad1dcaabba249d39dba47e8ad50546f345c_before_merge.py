    def spatial_shape(self):
        """Return spatial shape of first image in subject.

        Consistency of shapes across images in the subject is checked first.
        """
        return self.shape[1:]