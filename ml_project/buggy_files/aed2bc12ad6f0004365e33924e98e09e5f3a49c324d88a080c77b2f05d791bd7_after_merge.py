    def __init__(self, items: List['OverloadPart']) -> None:
        assert len(items) > 0
        self.items = items
        self.impl = None
        self.set_line(items[0].line)