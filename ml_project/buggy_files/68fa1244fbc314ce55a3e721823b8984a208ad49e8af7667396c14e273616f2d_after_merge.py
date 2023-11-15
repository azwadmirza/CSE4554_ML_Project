    def shape(self):
        """Return shape of first image in subject.

        Consistency of shapes across images in the subject is checked first.
        """
        self.check_consistent_attribute('shape')
        return self.get_first_image().shape