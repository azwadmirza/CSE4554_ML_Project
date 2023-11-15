    def set_description(self, desc=None):
        """
        Set/modify description of the progress bar.
        """
        self.desc = desc + ': ' if desc else ''