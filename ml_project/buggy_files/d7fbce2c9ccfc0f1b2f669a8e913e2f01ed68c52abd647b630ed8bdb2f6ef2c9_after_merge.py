    def __eq__(self, other):
        if not other:
            return False
        if hasattr(other, "parsed"):
            p2 = other.parsed
        else:
            p2, nm2 = self._parse_net(other)
        return self.parsed == p2