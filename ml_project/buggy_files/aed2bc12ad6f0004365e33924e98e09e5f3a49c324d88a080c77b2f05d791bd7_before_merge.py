    def __init__(self, items: List['OverloadPart']) -> None:
        self.items = items
        self.impl = None
        self.set_line(items[0].line)