    def __init__(self, items: List[Tuple[Expression, Expression]]) -> None:
        self.items = items
        # key is None for **item, e.g. {'a': 1, **x} has
        # keys ['a', None] and values [1, x].
        if all(x[0] and x[0].literal == LITERAL_YES and x[1].literal == LITERAL_YES
               for x in items):
            self.literal = LITERAL_YES
            self.literal_hash = (cast(Any, 'Dict'),) + tuple(
                (x[0].literal_hash, x[1].literal_hash) for x in items)