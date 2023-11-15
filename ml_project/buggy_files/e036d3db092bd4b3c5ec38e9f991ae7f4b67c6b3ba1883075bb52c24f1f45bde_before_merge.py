        def calculate_starts(dims: Tuple[Tuple[int, ...]]) -> Tuple[int, ...]:
            """Calculate starting indexes given dims."""
            s = [np.prod(d) for d in dims]
            starts = np.cumsum([0] + s)[: len(dims)]
            return tuple(int(i) for i in starts)