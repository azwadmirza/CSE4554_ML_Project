    def __hash__(self) -> int:
        return hash((ReprObject, self._value))