    def set_description(self, desc=None, refresh=True):
        """
        Set/modify description of the progress bar.
        Parameters
        ----------
        desc  : str, optional
        refresh  : bool, optional
            Forces refresh [default: True].
        """
        self.desc = desc + ': ' if desc else ''
        if refresh:
            self.refresh()