    def __init__(self, items: List['OverloadPart']) -> None:
        super().__init__()
        assert len(items) > 0
        self.items = items
        self.unanalyzed_items = items.copy()
        self.impl = None
        self.set_line(items[0].line)