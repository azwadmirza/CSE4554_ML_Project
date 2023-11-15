    def __init__(self, base: Expression, index: Expression) -> None:
        self.base = base
        self.index = index
        self.analyzed = None
        if self.index.literal == LITERAL_YES:
            self.literal = self.base.literal
            self.literal_hash = ('Index', base.literal_hash,
                                 index.literal_hash)