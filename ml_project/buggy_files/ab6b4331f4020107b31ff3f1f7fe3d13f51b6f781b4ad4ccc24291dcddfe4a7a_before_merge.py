    def format(self, name=False):
        """
        Render a string representation of the Index
        """
        header = []

        if name:
            header.append(str(self.name) if self.name is not None else '')

        return header + ['%s' % Period(x, freq=self.freq) for x in self]