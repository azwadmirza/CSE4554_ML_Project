    def num_relations(self) -> int:  # noqa: D401
        """The number of unique relations."""
        if self.create_inverse_triples:
            return 2 * self.real_num_relations
        return self.real_num_relations