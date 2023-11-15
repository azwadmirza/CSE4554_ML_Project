    def name(self) -> str:
        if self.items:
            return self.items[0].name()
        else:
            # This may happen for malformed overload
            assert self.impl is not None
            return self.impl.name()