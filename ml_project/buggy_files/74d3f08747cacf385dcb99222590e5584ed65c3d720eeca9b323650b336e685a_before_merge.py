    def apply(self, triples_factory: TriplesFactory) -> TriplesFactory:
        """Make a new triples factory containing neither duplicate nor inverse relationships."""
        return triples_factory.new_without_relations(self.relations_to_delete)