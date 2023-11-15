    def add_honest_makers(self, makers):
        """A maker who has shown willigness to complete the protocol
        by returning a valid signature for a coinjoin can be added to
        this list, the taker can optionally choose to only source
        offers from thus-defined "honest" makers.
        """
        self.honest_makers.extend(makers)