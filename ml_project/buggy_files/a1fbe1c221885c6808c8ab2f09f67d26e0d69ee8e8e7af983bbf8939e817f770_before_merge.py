    def query_types(self, types: Iterable[Type]) -> T:
        """Perform a query for a list of types.

        Use the strategy to combine the results.
        """
        return self.strategy(t.accept(self) for t in types)