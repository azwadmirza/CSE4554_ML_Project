    def __init__(self, name: str, old_type: 'Optional[mypy.types.Type]', line: int) -> None:
        self.name = name
        self.old_type = old_type