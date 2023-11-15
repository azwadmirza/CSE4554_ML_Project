    def __eq__(self, other):
        if not isinstance(other, HyKeyword):
            return NotImplemented
        return self.name == other.name