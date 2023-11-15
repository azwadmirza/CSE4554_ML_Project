    def __init__(self, items: List[Expression]) -> None:
        self.items = items
        if all(x.literal == LITERAL_YES for x in items):
            self.literal = LITERAL_YES
            self.literal_hash = ('Set',) + tuple(x.literal_hash for x in items)