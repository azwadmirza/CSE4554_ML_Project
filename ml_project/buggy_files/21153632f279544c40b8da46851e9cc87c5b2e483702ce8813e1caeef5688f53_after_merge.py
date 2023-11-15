    def calc_bounding_rect(self):
        """A rect object that contains all sprites of this group
        """
        rect = super(RelativeGroup, self).calc_bounding_rect()
        # return self.calc_absolute_rect(rect)
        return rect