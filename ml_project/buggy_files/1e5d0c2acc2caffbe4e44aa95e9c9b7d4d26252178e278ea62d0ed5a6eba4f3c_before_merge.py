    def __eq__(self, other):
        return isinstance(other, Loop) and other.header == self.header