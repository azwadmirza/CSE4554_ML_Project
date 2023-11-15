    def query_types(self, types: Iterable[Type]) -> T:
        """Perform a query for a list of types.

        Use the strategy to combine the results.
        Skip types already visited types to avoid infinite recursion.
        Note: types can be recursive until they are fully analyzed and "unentangled"
        in patches after the semantic analysis.
        """
        res = []  # type: List[T]
        for t in types:
            if any(t is s for s in self.seen):
                continue
            self.seen.append(t)
            res.append(t.accept(self))
        return self.strategy(res)