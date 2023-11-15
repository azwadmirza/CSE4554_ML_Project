    def __eq__(self, other):
        """Check for equality."""
        if isinstance(other, str):
            return self.name_match(self.name, other)
        elif isinstance(other, numbers.Number) or \
                isinstance(other, (tuple, list)) and len(other) == 3:
            return self.wavelength_match(self.wavelength, other)
        else:
            return super(DatasetID, self).__eq__(other)