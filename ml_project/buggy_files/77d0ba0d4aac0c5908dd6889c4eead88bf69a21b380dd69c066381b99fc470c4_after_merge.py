    def __gt__(self, other):
        return -self <= -(other + 1)