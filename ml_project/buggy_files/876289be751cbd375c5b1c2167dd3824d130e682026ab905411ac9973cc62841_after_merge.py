    def spacing(self):
        """Return spacing of first image in subject.

        Consistency of spacings across images in the subject is checked first.
        """
        self.check_consistent_attribute('spacing')
        return self.get_first_image().spacing