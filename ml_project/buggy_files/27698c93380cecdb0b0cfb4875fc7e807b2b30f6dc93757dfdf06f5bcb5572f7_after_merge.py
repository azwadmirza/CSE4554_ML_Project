    def __init__(self, items: List['OverloadPart']) -> None:
        super().__init__()
        self.items = items
        self.unanalyzed_items = items.copy()
        self.impl = None
        if len(items) > 0:
            self.set_line(items[0].line)
        self.is_final = False