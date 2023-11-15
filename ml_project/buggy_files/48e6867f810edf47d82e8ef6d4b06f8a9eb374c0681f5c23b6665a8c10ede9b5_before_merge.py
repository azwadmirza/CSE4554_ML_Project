    def add_ignored_makers(self, makers):
        """Makers should be added to this list when they have refused to
        complete the protocol honestly, and should remain in this set
        for the duration of the Taker run (so, the whole schedule).
        """
        self.ignored_makers.extend(makers)