    def create_lcwa_instances(self, use_tqdm: Optional[bool] = None) -> Instances:
        """Create LCWA instances for this factory's triples."""
        return LCWAInstances.from_triples(
            mapped_triples=self._add_inverse_triples_if_necessary(mapped_triples=self.mapped_triples),
            num_entities=self.num_entities,
        )