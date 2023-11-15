    def __hash__(self) -> int:
        return hash((type(self), self._value))