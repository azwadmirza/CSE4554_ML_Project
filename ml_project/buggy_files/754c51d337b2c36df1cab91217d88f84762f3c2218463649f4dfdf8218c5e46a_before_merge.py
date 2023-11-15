    def __eq__(self, other):
        if isinstance(other, GroupResult):
            return (
                other.id == self.id and
                other.results == self.results and
                other.parent == self.parent
            )
        return NotImplemented