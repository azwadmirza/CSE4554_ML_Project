    def __lt__(self, other):
        return abs(self.pos) < abs(other.pos)